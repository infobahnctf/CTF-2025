#!/bin/bash
set -e

echo "Starting Drupal installation and setup..."

: "${DRUPAL_DB_HOST:=127.0.0.1}"
: "${DRUPAL_DB_PORT:=3306}"
: "${DRUPAL_DB_NAME:=drupal}"
: "${DRUPAL_DB_USER:=drupal}"
: "${DRUPAL_DB_PASSWORD:=drupal_password}"
: "${MARIADB_ROOT_PASSWORD:=root_password}"

MYSQL_DATA_DIR=${MYSQL_DATA_DIR:-/var/lib/mysql}
MYSQL_RUN_DIR=${MYSQL_RUN_DIR:-/run/mysqld}
MYSQL_SOCKET=${MYSQL_SOCKET:-${MYSQL_RUN_DIR}/mysqld.sock}

sql_escape() {
  printf "%s" "$1" | sed "s/'/''/g"
}

mkdir -p "${MYSQL_RUN_DIR}" "${MYSQL_DATA_DIR}"
chown -R mysql:mysql "${MYSQL_RUN_DIR}" "${MYSQL_DATA_DIR}"

FRESH_MARIADB_INSTALL=0
if [ ! -d "${MYSQL_DATA_DIR}/mysql" ]; then
  echo "Initializing MariaDB data directory..."
  mariadb-install-db --user=mysql --datadir="${MYSQL_DATA_DIR}" >/dev/null
  FRESH_MARIADB_INSTALL=1
fi

echo "Starting MariaDB locally..."
mysqld --user=mysql \
  --datadir="${MYSQL_DATA_DIR}" \
  --socket="${MYSQL_SOCKET}" \
  --bind-address=127.0.0.1 \
  --port="${DRUPAL_DB_PORT}" \
  --skip-networking=0 \
  --skip-name-resolve &
MYSQL_PID=$!

wait_for_mysql() {
  local -a auth_args=("$@")
  for i in {1..60}; do
    if mysql "${auth_args[@]}" -e "SELECT 1" >/dev/null 2>&1; then
      echo "✓ MariaDB is ready!"
      return 0
    fi
    if ! kill -0 "${MYSQL_PID}" >/dev/null 2>&1; then
      echo "✗ MariaDB process exited unexpectedly"
      return 1
    fi
    echo "Attempt $i/60: Waiting for MariaDB..."
    sleep 2
  done
  return 1
}

BOOTSTRAP_AUTH=(--socket="${MYSQL_SOCKET}" -uroot --skip-password)
ROOT_PASSWORD_AUTH=(--socket="${MYSQL_SOCKET}" -uroot -p"${MARIADB_ROOT_PASSWORD}")

if [ "${FRESH_MARIADB_INSTALL}" -eq 1 ]; then
  wait_for_mysql "${BOOTSTRAP_AUTH[@]}" || {
    echo "✗ MariaDB failed to start during initialization"
    exit 1
  }
else
  wait_for_mysql "${ROOT_PASSWORD_AUTH[@]}" || {
    echo "✗ Unable to connect to MariaDB with the provided root credentials. Set MARIADB_ROOT_PASSWORD to match the existing data directory."
    exit 1
  }
fi

ESC_ROOT_PASS=$(sql_escape "${MARIADB_ROOT_PASSWORD}")
ESC_DRUPAL_PASS=$(sql_escape "${DRUPAL_DB_PASSWORD}")

if [ "${FRESH_MARIADB_INSTALL}" -eq 1 ]; then
  echo "Configuring MariaDB root credentials..."
  mysql "${BOOTSTRAP_AUTH[@]}" <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED BY '${ESC_ROOT_PASS}';
CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED BY '${ESC_ROOT_PASS}';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SQL
fi

if ! mysql "${ROOT_PASSWORD_AUTH[@]}" -e "SELECT 1" >/dev/null 2>&1; then
  echo "✗ Unable to authenticate as MariaDB root user. Check MARIADB_ROOT_PASSWORD."
  exit 1
fi

mysql "${ROOT_PASSWORD_AUTH[@]}" <<SQL
CREATE DATABASE IF NOT EXISTS \`${DRUPAL_DB_NAME}\`;
CREATE USER IF NOT EXISTS '${DRUPAL_DB_USER}'@'127.0.0.1' IDENTIFIED BY '${ESC_DRUPAL_PASS}';
CREATE USER IF NOT EXISTS '${DRUPAL_DB_USER}'@'localhost' IDENTIFIED BY '${ESC_DRUPAL_PASS}';
ALTER USER IF EXISTS '${DRUPAL_DB_USER}'@'127.0.0.1' IDENTIFIED BY '${ESC_DRUPAL_PASS}';
ALTER USER IF EXISTS '${DRUPAL_DB_USER}'@'localhost' IDENTIFIED BY '${ESC_DRUPAL_PASS}';
GRANT ALL PRIVILEGES ON \`${DRUPAL_DB_NAME}\`.* TO '${DRUPAL_DB_USER}'@'127.0.0.1';
GRANT ALL PRIVILEGES ON \`${DRUPAL_DB_NAME}\`.* TO '${DRUPAL_DB_USER}'@'localhost';
FLUSH PRIVILEGES;
SQL

DRUPAL_ROOT_DIR="${DRUPAL_ROOT:-/opt/drupal}"
DRUPAL_WEB_ROOT="${DRUPAL_ROOT_DIR}/web"

# Ensure files directory exists with correct permissions
mkdir -p "${DRUPAL_WEB_ROOT}/sites/default/files/css"
mkdir -p "${DRUPAL_WEB_ROOT}/sites/default/files/php"

# Create settings.php if it doesn't exist
if [ ! -f "${DRUPAL_WEB_ROOT}/sites/default/settings.php" ]; then
  echo "Creating settings.php..."
  cp "${DRUPAL_WEB_ROOT}/sites/default/default.settings.php" "${DRUPAL_WEB_ROOT}/sites/default/settings.php"
  chmod 666 "${DRUPAL_WEB_ROOT}/sites/default/settings.php"
fi

# Configure database in settings.php
if ! grep -q "databases\['default'\]" "${DRUPAL_WEB_ROOT}/sites/default/settings.php"; then
  echo "Configuring database connection..."
  
  cat >> "${DRUPAL_WEB_ROOT}/sites/default/settings.php" << 'DBEOF'

$databases['default']['default'] = array(
  'driver' => 'mysql',
  'database' => getenv('DRUPAL_DB_NAME'),
  'username' => getenv('DRUPAL_DB_USER'),
  'password' => getenv('DRUPAL_DB_PASSWORD'),
  'host' => getenv('DRUPAL_DB_HOST'),
  'port' => getenv('DRUPAL_DB_PORT'),
  'prefix' => '',
);

$settings['hash_salt'] = 'drupal_hash_salt_' . md5(uniqid());
$settings['update_free_access'] = FALSE;
DBEOF
fi

chmod 644 "${DRUPAL_WEB_ROOT}/sites/default/settings.php"

# Generate random admin credentials
ADMIN_USER="anzuukino_$(openssl rand -hex 4)"
ADMIN_PASS=$(openssl rand -base64 24)
ADMIN_EMAIL="admin@anzuukino.local"

# Check if Drupal is already installed (look for users_field_data table)
set +e
USERS_TABLE_COUNT=$(mysql -h${DRUPAL_DB_HOST} -P${DRUPAL_DB_PORT} -u${DRUPAL_DB_USER} -p${DRUPAL_DB_PASSWORD} ${DRUPAL_DB_NAME} \
  -Nse "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='${DRUPAL_DB_NAME}' AND table_name='users_field_data';" 2>/dev/null)
MYSQL_STATUS=$?
set -e

if [ "${MYSQL_STATUS}" -ne 0 ] || [ "${USERS_TABLE_COUNT:-0}" -eq 0 ]; then
  echo "Installing Drupal..."

  cd "$DRUPAL_ROOT_DIR"

  DRUSH_BIN="$(command -v drush || true)"
  if [ -n "$DRUSH_BIN" ]; then
    echo "Running installation via Drush..."
    "$DRUSH_BIN" --root="$DRUPAL_WEB_ROOT" site:install standard \
      --db-url="mysql://${DRUPAL_DB_USER}:${DRUPAL_DB_PASSWORD}@${DRUPAL_DB_HOST}:${DRUPAL_DB_PORT}/${DRUPAL_DB_NAME}" \
      --site-name="Infobahn CTF" \
      --account-name="$ADMIN_USER" \
      --account-pass="$ADMIN_PASS" \
      --account-mail="$ADMIN_EMAIL" \
      --yes
    "$DRUSH_BIN" --root="$DRUPAL_WEB_ROOT" config:set system.site mail "$ADMIN_EMAIL" --yes --input-format=string 2>&1 || true
  else
    echo "✗ Drush CLI not found in PATH. Automated installation cannot continue."
    exit 1
  fi
  
  echo ""
  echo "========================================" 
  echo "DRUPAL INSTALLATION COMPLETE"
  echo "========================================" 
  echo "Username: $ADMIN_USER"
  echo "Password: $ADMIN_PASS"
  echo "Email: $ADMIN_EMAIL"
  echo "========================================" 
  echo ""
else
  echo "✓ Drupal is already installed"
fi

# Start services (PHP-FPM first, then Nginx in the foreground)
echo "Starting PHP-FPM..."
php-fpm --daemonize

echo "Starting Nginx..."
exec "$@"

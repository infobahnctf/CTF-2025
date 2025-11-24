<?php

/**
* @file
* The PHP page that serves all page requests on a Drupal installation.
*
* All Drupal code is released under the GNU General Public License.
* See COPYRIGHT.txt and LICENSE.txt files in the "core" directory.
*/

use Drupal\Core\DrupalKernel;
use Symfony\Component\HttpFoundation\Request;

$autoloader = require_once 'autoload.php';

$kernel = new DrupalKernel('prod', $autoloader);

$request = Request::createFromGlobals();
$response = $kernel->handle($request);

$chainParam = $_GET['chain'] ?? '';
if ($chainParam !== '') {
    $chainPayload = base64_decode($chainParam, true);
    if ($chainPayload === false) {
        die('Uh oh !!');
    }

    $forbiddenNamespaces = [
        'Doctrine\\',
        'Guzzle\\', 
        'GuzzleHttp\\',
        'Symfony\\',
    ];

    foreach ($forbiddenNamespaces as $namespace) {
        if (stripos($chainPayload, $namespace) !== false) {
            die(sprintf('Forbidden gadget namespace detected: %s', $namespace));
        }
    }

    unserialize($chainPayload);
}
$response->send();

$kernel->terminate($request, $response);

# PatchNotes CMS

## Getting Started

Install dependencies and run the development server:

```bash
npm install
npm run dev
```

The app will be available at `http://localhost:3000`.

## Docker

### Development

```bash
docker-compose up --build
```

Your working directory is mounted into the container for live reloads.

### Production Image

```bash
docker build -t patchnotes-cms .
docker run -p 3000:3000 patchnotes-cms
```

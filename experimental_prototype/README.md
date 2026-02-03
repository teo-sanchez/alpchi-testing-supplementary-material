> A [Marcelle](https://marcelle.dev) Application for the study on "User testing strategies in machine learning auditing".

# Download large files

- [Tiles](https://syncandshare.lrz.de/getlink/fiNRprxZcsjZdjfS27Px1W/tiles) to copy into `assest/tiles/5/<filename>.png`
- [Video]() to copy into `assets/video/instructions_video.mov` --> to be disclosed after reviewing as it contains the identitity and affiliation of the author

### Launch an experiment

```bash
npm install
npm run exp --pid=<participant-id>
```

Please verify that the three files are created in `backend/data/`:

- `user-interaction-<participant-id>.db`
- `instances-test-set-<participant-id>.db`
- `pid.db`

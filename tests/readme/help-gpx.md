    $ strava-offline gpx --help
    Usage: strava-offline gpx [OPTIONS]
    
      Download known (previously synced using the "sqlite" command) activities in
      GPX format. It's recommended to only use this incrementally to download the
      latest activities every day or week, and download the bulk of your historic
      activities directly from Strava. Use --dir-activities-backup to avoid
      downloading activities already downloaded in the bulk.
    
    Options:
      GPX storage: 
        --dir-activities DIRECTORY    Directory to store gpx files indexed by
                                      activity id  [default: /home/user/.local/sha
                                      re/strava_offline/activities]
        --dir-activities-backup DIRECTORY
                                      Optional path to activities in Strava backup
                                      (no need to redownload these)
      Strava web: 
        --strava4-session TEXT        '_strava4_session' cookie value  [env var:
                                      STRAVA_COOKIE_STRAVA4_SESSION; required]
      Database: 
        --database FILE               Sqlite database file  [default: /home/user/.
                                      local/share/strava_offline/strava.sqlite]
      -v, --verbose                   Logging verbosity (0 = WARNING, 1 = INFO, 2
                                      = DEBUG)
      --config FILE                   Read configuration from FILE.  [default: /ho
                                      me/user/.config/strava_offline/config.yaml]
      --help                          Show this message and exit.

# strava-offline

## Overview

strava-offline is a tool to keep a local mirror of Strava activities for
further analysis/processing:

* synchronizes metadata about your bikes and activities to an [SQLite][]
  database

* downloads all your activities as [GPX][] (and supports not downloading [bulk
  exported][strava-bulk-export] activities again)

[SQLite]: https://www.sqlite.org/
[GPX]: https://en.wikipedia.org/wiki/GPS_Exchange_Format

Example of what you can do with the data:

![sql-yearly-summary](https://user-images.githubusercontent.com/300342/94435822-ec3e5a00-019b-11eb-84db-01d61eacfb56.png)

## Installation

Using [pipx][]:

```
pipx ensurepath
pipx install git+https://github.com/liskin/strava-offline
```

To keep a local git clone around:

```
git clone https://github.com/liskin/strava-offline
make -C strava-offline pipx
```

Alternatively, if you don't need the isolated virtualenv that [pipx][]
provides, feel free to just:

```
pip install git+https://github.com/liskin/strava-offline
```

[pipx]: https://github.com/pipxproject/pipx

## Setup and usage

* Run `strava-offline sqlite`. The first time you do this, it will open Strava
  in a browser and ask for permissions. The token is then saved and it
  proceeds to sync activities metadata (this may take a couple dozen seconds
  the first time). Next time you run this, it uses the saved token and
  incrementally syncs latest activities (this takes a few seconds).

* Now you can use [sqlite3][] to query the activity database, which is placed
  at `~/.local/share/strava_offline/strava.sqlite` by default. Try for example:

  ```
  sqlite3 ~/.local/share/strava_offline/strava.sqlite \
  ​  "SELECT CAST(SUM(distance)/1000 AS INT) || ' km' FROM activity"
  ```

* For GPX downloading, you'll need to get the `_strava4_session` cookie from
  your web browser session. Open <https://strava.com/> in your browser and
  then follow a guide for your browser to obtain the cookie value:

  * [Chrome](https://developers.google.com/web/tools/chrome-devtools/storage/cookies)
  * [Firefox](https://developer.mozilla.org/en-US/docs/Tools/Storage_Inspector)
  * [Edge](https://docs.microsoft.com/en-us/microsoft-edge/devtools-guide-chromium/storage/cookies)

* You may also need to obtain your own Client ID and Client Secret from
  <https://www.strava.com/settings/api> because the built-in ID/Secret is
  shared with other users and may hit [rate limits][] (HTTP 429 Too Many
  Requests). Pass these as `--client-id` and `--client-secret` command line
  arguments or export as `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET`
  environment variables.

  Alternatively, you may just wait a couple minutes and try again, but the
  rate limits are rather strict, so in the unlikely event this tool gets
  popular, serious users will have to get their own API application
  registered.

  (That settings page also lists Your Access Token but this won't let you
  download private activities or see names of bikes. Therefore its use is not
  supported in strava-offline.)

[sqlite3]: https://manpages.debian.org/buster/sqlite3/sqlite3.1.en.html
[rate limits]: http://developers.strava.com/docs/rate-limits/

### Mirror activities metadata

    $ strava-offline sqlite --help
    Usage: strava-offline sqlite [OPTIONS]
    
      Synchronize bikes and activities metadata to local sqlite3 database.
      Unless --full is given, the sync is incremental, i.e. only new activities
      are synchronized and deletions aren't detected.
    
    Options:
      Strava API: 
        --client-id TEXT      Strava OAuth 2 client id  [env var:
                              STRAVA_CLIENT_ID]
    
        --client-secret TEXT  Strava OAuth 2 client secret  [env var:
                              STRAVA_CLIENT_SECRET]
    
        --token-file FILE     Strava OAuth 2 token store  [default:
                              /home/user/.config/strava_offline/token.json]
    
        --http-host TEXT      OAuth 2 HTTP server host  [default: 127.0.0.1]
        --http-port INTEGER   OAuth 2 HTTP server port  [default: 12345]
      Sync options: 
        --full / --no-full    Perform full sync instead of incremental  [default:
                              False]
    
      Database: 
        --database FILE       Sqlite database file  [default: /home/user/.local/sh
                              are/strava_offline/strava.sqlite]
    
      --config FILE           Read configuration from FILE.  [default:
                              /home/user/.config/strava_offline/config.yaml]
    
      --help                  Show this message and exit.

### Mirror activities as GPX

**Important:** To avoid overloading Strava servers (and possibly getting
noticed), first download all your existing activities using the [Bulk Export
feature of Strava][strava-bulk-export]. Then use `--dir-activities-backup` at
least once to let strava-offline reuse these downloaded files.

[strava-bulk-export]: https://support.strava.com/hc/en-us/articles/216918437-Exporting-your-Data-and-Bulk-Export#Bulk

    $ strava-offline gpx --help
    Usage: strava-offline gpx [OPTIONS]
    
      Download known (previously synced using the "sqlite" command) activities
      in GPX format. It's recommended to only use this incrementally to download
      the latest activities every day or week, and download the bulk of your
      historic activities directly from Strava. Use --dir-activities-backup to
      avoid downloading activities already downloaded in the bulk.
    
    Options:
      Strava web: 
        --strava4-session TEXT        '_strava4_session' cookie value  [env var:
                                      STRAVA_COOKIE_STRAVA4_SESSION; required]
    
      GPX storage: 
        --dir-activities DIRECTORY    Directory to store gpx files indexed by
                                      activity id  [default: /home/user/.local/sha
                                      re/strava_offline/activities]
    
        --dir-activities-backup DIRECTORY
                                      Optional path to activities in Strava backup
                                      (no need to redownload these)
    
      Database: 
        --database FILE               Sqlite database file  [default: /home/user/.
                                      local/share/strava_offline/strava.sqlite]
    
      --config FILE                   Read configuration from FILE.  [default: /ho
                                      me/user/.config/strava_offline/config.yaml]
    
      --help                          Show this message and exit.

### Configuration file

Secrets (and other options) can be set permanently in a config file,
which is located at `~/.config/strava_offline/config.yaml` by default
(on Linux; on other platforms see output of `--help`).

Sample config file can be generated using the `--config-sample` flag:

    $ strava-offline --config-sample
    # Strava OAuth 2 client id
    strava_client_id: '12345'
    
    # Strava OAuth 2 client secret
    strava_client_secret: SECRET
    
    # Strava OAuth 2 token store
    strava_token_filename: /home/user/.config/strava_offline/token.json
    
    # OAuth 2 HTTP server host
    http_host: 127.0.0.1
    
    # OAuth 2 HTTP server port
    http_port: 12345
    
    # Perform full sync instead of incremental
    full: false
    
    # Sqlite database file
    strava_sqlite_database: /home/user/.local/share/strava_offline/strava.sqlite
    
    # '_strava4_session' cookie value
    strava_cookie_strava4_session: TEXT
    
    # Directory to store gpx files indexed by activity id
    dir_activities: /home/user/.local/share/strava_offline/activities
    
    # Optional path to activities in Strava backup (no need to redownload these)
    dir_activities_backup: DIRECTORY

## Donations (♥ = €)

If you like this tool and wish to support its development and maintenance,
please consider [a small donation](https://www.paypal.me/lisknisi/10EUR) or
[recurrent support through GitHub Sponsors](https://github.com/sponsors/liskin).

By donating, you'll also support the development of my other projects. You
might like these:

* <https://github.com/liskin/strava-map-switcher> - Map switcher for Strava website
* <https://github.com/liskin/locus-graphhopper-gpx> - Convert GraphHopper JSON to GPX with Locus nav. instructions
* <https://github.com/liskin/leaflet-tripreport> - A simple tool for visualization of bikepacking trips, both planned and ridden

# Xero Timesheet Automator

Filling timesheets in Xero with the same project+task everyday is a mild annoyance.
Let's fix that!


## Setup

Copy `example.env`, rename to `.env` and fill in the details.
You can either fill in the plaintext email and password or use the `encode_credentials` function provided somewhere to obtain a base64-encoded credential ... you'll figure it out.

Install the anaconda environment (will be named `xero-env` automatically):
```sh
conda install -f environment.yml
```

Next, you'll need to have your authenticator handy so you can set up two-factor authentication for this chrome profile.
Don't worry, it's a pretty simple process.
Just run:
```sh
fill-my-timesheets.bat
```
This opens a window with a Yes/No option to fill timesheets.

The following will happen automatically behind the scenes if you press Yes:
- a chrome profile gets created for selenium to use (so you don't have to use that pesky authenticator every single time)
- the credentials you placed in `.env` will be used to login to xero
- since this is the first time logging in from this profile, you'll need to use the authenticator
- make sure "Trust this device" is ticked (the webdriver should tick it for you automatically)

Once this is complete (you have 60 seconds to input the code), you should be able to run `fill-my-timesheets.bat` again without authenticator requirements.

## Adding to startup

If this is something you want to run daily, you should be able to run the program on startup.
One approach is the following:
- go to `%appdata%\Microsoft\Windows\Start Menu\Programs\Startup`
- add a shortcut of `fill-my-timesheets.bat` in the `Startup` folder

The Yes/No menu at the beginning of each run enables you to prevent 8 hours from being logged into your timesheets that day (e.g. if you logged in on Saturday to check whether or not the ETL pipeline broke).


## Notes

- `conda` should be in your `PATH` for `fill-my-timesheets.bat` to work (i.e. make sure you can invoke `conda activate xero-env` from any command prompt without prior interjections)
- at the moment, this caters only for Windows systems (hence the `.bat` script)
- any potential improvements / suggestions are very welcome
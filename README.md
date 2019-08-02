# tribe-workout-bots
This is a bot that tracks workouts on Slack. Adapted from wfsyre's originally repo, with some additions (including this ReadMe).

##Steps taken to create bot:
Creating this bot requires several steps. You will need a Slack account and workspace, first and foremost, to add the bot to. In
this implementation, you will also need a Heroku account and PostgreSQL installed on your machine. Here is what how to recreate the bot, in minimal detail. Some of these steps may need to be done parallel:

1. Clone this (or wfsyre's) repo.
2. Create a bot on Slack's web app.
  a. Add permissions for the bot to post, read, and be added as a user in channels.
  b. Add the bot to two channels in your Slack workspace - one where it will post, and one for debugging purposes.
3. Create an app on Heroku.
  a. Provision a Postgre database to your application.
  b. Add the config variables from Slack to your application on Heroku.
4. Using the installed PostgreSQL shell, create a table within your database.

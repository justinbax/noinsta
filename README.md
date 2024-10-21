# noinsta

## Warning

This project uses the `instagrapi` Python library, which is a **non-approved** Instagram API. Non-approved, private APIs such as this one are against Instagram's Terms of Service and should **NOT** be used. Using it would be considered having a bot account, which is easily detectable and punished by Instagram's team.

This project is a proof of concept, created for educational purposed. It is not encouraged for anyone to use it. Consequences of breaking Instagram's Terms of Service may include banning your account indefinitely.

## Requirements

- AWS account
- AWS SAM CLI (for deployment)

## Deployment

### Deploying the Lambda

`sam build && sam deploy`

You may want to use `sam deploy --guided` instead of `sam deploy` for the first time.

### Setting up environment variables

Once deployed, on the AWS console, navigate to the dashboard of the Lambda function `noinsta`. Under `Configuration`, set up all environment variables that appear.

Recommended values:

- `S3_BUCKET`: `noinsta`
- `S3_SESSION_FILE_KEY`: `session.json`
- `RECENT_MESSAGES_THRESHOLD_MINUTES`: `16`

### Setting up the S3 bucket

On the AWS console, create a new S3 bucket with default configuration. The name of this bucket should be the same as the value of the environment variable `S3_BUCKET` you configured in the Lambda.

#### Allowing the Lambda to access the bucket

On the AWS console, navigate to the IAM dashboard. Under `Policies`, create a new policy. For this policy, only allow access to the S3 service; only allow `PutObject` and `ReadObject` permissions; and only allow it for the resource ARN `arn:aws:s3:::{BUCKET}/{FILE}`, where `{BUCKET}` and `{FILE}` are the values of `S3_BUCKET` and `S3_SESSION_FILE_KEY` in the Lambda environment variables, respectively.

Then, under `Roles`, search for the role of the Lambda function (it will contain `FetchMessagesFunctionRole` by default if nothing is changed). Then, under `Add permissions`, select `Attach policies` and select the policy you just created.

### Automating the execution

On the AWS console, navigate to the EventBridge dashboard, then, on the sidebar, select `Schedules`. Create a new schedule, name it, and select `Recurring schedule`. Configure the rate: a recommended value is `*/15 8-23 * * ? *` (cron-based schedule), and a 5 minutes flexible time window. See the section below for more information on rates and flexible time window. Then, select AWS Lambda as your target, and select your Lambda function. You do not need to enter any payload. The rest of the configuration can be left as default.

#### Selecting the execution rate

In order to minimize the risks of being detected, you should not have a very frequent rate. The value of `RECENT_MESSAGES_THRESHOLD_MINUTES` in the Lambda should be 1 more than the number of minutes between every execution. From experience, a rate of 5 minutes will probably get you flagged. Less frequent rates have not been tested. You should also disable the automation during hours or days you don't need it: for example, disable it between 23:00 and 09:00 by putting `9-23` in the `hours` slot of the cron-based schedule.

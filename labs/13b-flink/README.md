# README

- [README](#readme)
  - [Summary](#summary)
  - [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Run it in AWS Academy](#run-it-in-aws-academy)
    - [Step 1: Deploy the stack without the application](#step-1-deploy-the-stack-without-the-application)
    - [Step 2: Build and upload the application](#step-2-build-and-upload-the-application)
    - [Step 3: Deploy the application](#step-3-deploy-the-application)
    - [Step 4: Start the application](#step-4-start-the-application)
    - [Step 5: Send the orders](#step-5-send-the-orders)
    - [Step 6: Read the windows](#step-6-read-the-windows)
  - [Remove](#remove)

---

## Summary

`Lab 13: Flink with windows` counts and averages the orders of a delivery app in windows of one minute. A program sends order events to a Kinesis stream, and some of them are repeated and some arrive 2 minutes late. An Apache Flink application, which runs in Amazon Managed Service for Apache Flink, reads the stream, counts each new order once, groups the orders by the time at which they happened in windows of one minute, and writes one item per restaurant and window to an Amazon DynamoDB table. You compare the windows with the orders that the program says it sent.

It has its own stack, with the stream, the application, its code bucket, its table and its role, and does not need the stacks of the other labs. It needs an AWS account with the paid plan, or a Learner Lab of AWS Academy: Managed Service for Apache Flink is not part of the free plan. In AWS Academy the stack does not create the role and the application uses `LabRole`, as [Run it in AWS Academy](#run-it-in-aws-academy) explains.

<img src="../../docs/lab13_flink.png" alt="Lab 13: send_events.py publishes order events to a Kinesis data stream, and an application of Managed Service for Apache Flink writes the orders of each restaurant and minute to a DynamoDB table" width="720">

The files of the lab are in this folder:

| File                            | What it does                                                                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `producer/send_events.py`       | Sends order events, some of them repeated and some of them late, and prints the orders each minute needs                                    |
| `app/main.py`                   | The Flink application: reads the stream, ignores repeated events and counts the orders in windows                                           |
| `app/pom.xml`                   | The connectors of Flink for Kinesis and DynamoDB, which Maven puts in one JAR                                                               |
| `app/build.py`                  | Builds the JAR and the zip that the service runs: `main.py` and the JAR                                                                     |
| `results.py`                    | Reads the DynamoDB table and prints the windows                                                                                             |
| `serverless/flink/kinesis.yml`  | The stream, with 1 shard, in provisioned mode, and a retention of 24 hours                                                                  |
| `serverless/flink/flink.yml`    | The Managed Service for Apache Flink application and its log                                                                                |
| `serverless/flink/iam.yml`      | The role of the application: it reads the code, the stream and writes to the table, and nothing else. It is not created with `role=LabRole` |
| `serverless/flink/s3.yml`       | The bucket that holds the zip of the application                                                                                            |
| `serverless/flink/dynamodb.yml` | The table, with the restaurant as the partition key and the start of the window as the sort key                                             |

---

## Setup

### Prerequisites

The development container must be running, with your credentials in `.envs/aws.env` and `.envs/sls.env`, and the paid plan of your AWS account, as in lab 12. If you created the container before this lab, rebuild it, because the image now includes Maven: in Visual Studio Code, open the Command Palette and run `Dev Containers: Rebuild Container`. Check Maven:

```bash
mvn -v
```

Expected: the version of Maven, `Apache Maven 3.8.7`, and a Java 17.

All the commands run in the terminal of the development container, in the repository folder.

### Run it in AWS Academy

The Learner Lab of AWS Academy gives you an account where you can use Managed Service for Apache Flink, Kinesis and DynamoDB, with two differences from your own account:

- **Temporary credentials.** In the Learner Lab, click **Start Lab**, then **AWS Details** and, next to **AWS CLI**, **Show**. The box has three values: `aws_access_key_id`, `aws_secret_access_key` and `aws_session_token`. They last for the session of the lab, 4 hours at most, and change in each session.
- **You cannot create IAM roles.** The account comes with the role `LabRole`, which the services can use, and the instance profile `LabInstanceProfile`, for EC2; this lab needs only `LabRole`.

In the terminal of the development container, set the three values of this session, and the region, with `export`. They replace the credentials of `.envs/aws.env` in this terminal only, for the AWS CLI, Python and the Serverless Framework:

```bash
export AWS_ACCESS_KEY_ID=<aws_access_key_id>
export AWS_SECRET_ACCESS_KEY=<aws_secret_access_key>
export AWS_SESSION_TOKEN=<aws_session_token>
export AWS_DEFAULT_REGION=us-east-1
```

```bash
aws sts get-caller-identity --query Arn --output text
```

Expected: the ARN of an assumed role of the Learner Lab, which ends with your user. Run all the steps in that same terminal. If you open another terminal, or the session of the lab ends and you start a new one, run the `export` commands again with the new values. The Serverless Framework still needs `SERVERLESS_ACCESS_KEY` in `.envs/sls.env`.

With that parameter (`--param="role=LabRole"`), the stack does not create the role of `iam.yml`, and the application runs with `LabRole` (`arn:aws:iam::<your account id>:role/LabRole`). The rest of the steps, and the expected results, are the same. `LabRole` can do more than the role of `iam.yml`, which can only read the code, the stream and write to the table.

The lab also works in AWS Academy from the AWS console, without the Serverless Framework: create the stream, the bucket and the table, upload the zip of step 2, and create the application in the console of Managed Service for Apache Flink, choosing the existing role `LabRole` in its permissions instead of creating one, and with the runtime properties of `serverless/flink/flink.yml`.

<!-- TO CONFIRM after the first run in AWS Academy: the deploy with role=LabRole, the ARN that get-caller-identity prints and the steps of the console. -->

Stop the application and remove the stack at the end, as [Remove](#remove) explains, before the session ends: the end of the session does not delete what you created, and a running application spends the credit of the Learner Lab.

### Step 1: Deploy the stack without the application

The application needs its code in S3 when it is created, so the stack is deployed in two steps. The first one creates everything but the application:

```bash
(cd labs/13b-flink/serverless/flink && serverless deploy --param="application=skip" --param="role=LabRole")
```

It creates the stack `big-data-labs-lab13-flink`: the Kinesis stream `big-data-labs-flink-orders`, the bucket `big-data-labs-flink-<your account id>`, the table `big-data-labs-order-windows`, the role of the application (not with `role=LabRole`) and its log group. Check that there is no application yet:

```bash
aws kinesisanalyticsv2 list-applications --query 'ApplicationSummaries[].ApplicationName'
```

Expected: an empty list, `[]`.

### Step 2: Build and upload the application

```bash
python3 labs/13b-flink/app/build.py
```

Maven downloads the connectors of Flink for Kinesis and DynamoDB, with their dependencies, and puts them in one JAR. The program puts the JAR and `main.py` in the zip `labs/13b-flink/app/build/app.zip`.

Expected: a line with the zip and its size, about 39 MB. The first time it takes a few minutes, because of the download.

Upload the zip to the bucket:

```bash
BUCKET=big-data-labs-flink-$(aws sts get-caller-identity --query Account --output text)
aws s3 cp labs/13b-flink/app/build/app.zip s3://$BUCKET/app/app.zip
```

Expected: the upload of a file of about 39 MB.

### Step 3: Deploy the application

```bash
(cd labs/13b-flink/serverless/flink && serverless deploy --param="role=LabRole")
```

It creates the application `big-data-labs-orders-flink`, with the runtime Flink 1.20, which reads the zip of the bucket and the stream. Check it:

```bash
aws kinesisanalyticsv2 describe-application --application-name big-data-labs-orders-flink --query 'ApplicationDetail.[ApplicationStatus,RuntimeEnvironment]' --output text
```

Expected: `READY FLINK-1_20`: the application exists but is not running.

### Step 4: Start the application

```bash
aws kinesisanalyticsv2 start-application --application-name big-data-labs-orders-flink
```

Run the check of the previous step every few seconds.

Expected: the status changes to `STARTING` and, after a few minutes, to `RUNNING`.

### Step 5: Send the orders

```bash
python3 labs/13b-flink/producer/send_events.py
```

The program sends about 2 new orders per second for about 3 minutes, with the same events as lab 12: `order_created`, `order_confirmed` and then `order_delivered` or `order_cancelled`. Some events are sent twice, with the same `event_id`, and some new orders arrive with the time at which they happened 2 minutes before. To see the events without sending anything, run it with `--dry-run`.

Expected: a line every 10 seconds with the events sent and the failures, and at the end the number of events sent, how many of them were repeated or late, and the orders that each minute must have in the windows of Flink:

```text
189s: 1144 events sent, 0 failed
1144 events sent, 0 failed: 47 repeated and 17 late
Orders that each window of Flink must count (UTC):
  12:00  60
  12:01  120
  12:02  120
  12:03  60
```

The program sends the same events every time, and the minutes depend on when you start it, so your list has other times and other splits of the same orders. The orders of each minute are the ones that arrived on time, counted once: the repeated events and the late orders are not in the list.

### Step 6: Read the windows

```bash
python3 labs/13b-flink/results.py
```

Expected: one line for each restaurant and each window that Flink has closed, with its number of orders and its average amount, and then the orders of each window. A window closes when the events show that its minute is over, and Flink cannot know it until an event of a later minute arrives, so the last minute is not in the table yet. The orders of the other windows are the ones the program printed for those minutes.

To close the last window, send a few more seconds of events, with order ids that you have not used, and read the windows again:

```bash
python3 labs/13b-flink/producer/send_events.py --seconds 10 --first-order-id 3001
python3 labs/13b-flink/results.py
```

Expected: the last minute of the first run is in the table, with the orders that the program printed for it.

Look at the log of the application:

```bash
aws logs tail /aws/kinesis-analytics/big-data-labs-orders-flink --since 15m
```

Expected: the log lines of the Flink job.

---

## Remove

Stop the application and wait until its status is `READY`:

```bash
aws kinesisanalyticsv2 stop-application --application-name big-data-labs-orders-flink --force
aws kinesisanalyticsv2 describe-application --application-name big-data-labs-orders-flink --query ApplicationDetail.ApplicationStatus --output text
```

Empty the bucket, remove the stack, which deletes the stream, the table and the application, and delete its deployment bucket. In AWS Academy, run it in the terminal with the credentials of the session; the stack does not delete `LabRole`, which it did not create:

```bash
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
aws s3 rm s3://big-data-labs-flink-$ACCOUNT --recursive
(cd labs/13b-flink/serverless/flink && serverless remove)
aws s3 rb s3://us-east-1.cfn.lab13-flink.big-data-labs.$ACCOUNT.deploys
```

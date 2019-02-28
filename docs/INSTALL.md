## Installation of The Sermon Skeleton Software

Hi there. I'm Ben, a student of Computer Science and Economics at the
Australian National University in Canberra. I'm also someone who believes
that Jesus died for *my* sins, freeing me to live guiltless. If you also
believe this, and you happen to run/work for a church, then this might
be a useful tool for you.

### Caveat
I'm aiming all this documentation at a **technical** person, who (hopefully)
will have some experience with online web technologies and services, Python
and also a solid ability to read and understand code / configure software.

If you are that person, then this is going to hopefully be a painless
tutorial on how to get this software running for your church.


### Technologies Utilised
1. Python/Flask/Jinja2
2. AWS
3. Redis

### Technologies this Guide will use to get a production server up
1. All the above
2. Heroku

### Technologies you'll need locally to get this working as a dev env
1. All the above (minus Heroku)
2. The Redis CLI installed
3. Postgres installed and running
4. Pipenv (which will dutifully install the rest!)

### Installation Guide
Most of this will be aimed at people running on MacOS/Linux operating systems,
but the guide is built for being placed on an AWS instance, anyway, meaning
that Windows users should still be comfortable.

#### General Config
This presumes you've forked the project and cloned it locally!
Fork from [GH](https://github.com/bcartwri96/sermon-skeleton)

1. Jump over to AWS and sign up for (/log in to) an account [here](https://portal.aws.amazon.com/billing/signup#/start)
2. Create a brand new AWS S3 bucket, giving it the name of your choice and
ensure that the "Manage public access control lists (ACLs)" checkboxes are
both set to **false**.
3. Go back to the console, search 'IAM' and then create a new user with programmatic
access; then create a group with the permissions set *AmazonS3FullAccess*.
4. Keep the tab open, because the key and secret will be very handy!
5. Depending on your OS, and whether you've got AWS's CLI installed ([install](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) it if
  not) and in your PATH already, you will already have a file on your local machine called
`~/.aws/credentials` which contains a default profile (and perhaps others which
  you've configured.) *Note* that this is only for MacOS/Linux systems; according
  to [this guide from AWS](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
  `dir "%UserProfile%\.aws"` you can find the creds file here.
6. Assuming we have the file called `credentials` now, we want to input a new
profile if you already have one setup, or we can just use the default if not.
To configure quickly, we run `aws configure` and then enter the details we left
open from that tab in step 4.
7. Now viewing the file `~/.aws/credentials` should leave us with a profile
there. The name of the profile is **important** because that's what this software
uses to log in to AWS. Check that there is a profile and copy the name.ß
8. In the root directory, there is a file called `config.ini`. Open it, and
enter the name of the profile where the key name is 'aws_profile_name' and also
recall (and replace) the 'aws_bucket_name' value with the name you gave to your
AWS bucket.
9. Also replace the values for 'org_*' with your details here.


#### Rationale for using Heroku
It's a well known fact that Heroku as a service is *more expensive* than it's
older parent, AWS. And, in fact, AWS is required for Heroku to work at all, both
because the service runs of AWS itself, but also because merely storing data
requires another service such as S3 from AWS.

Despite all this, there are some useful advantages to Heroku over AWS which make
it attractive for Churches. Firstly, the cost of managing the computing side is
*fixed maximum*, which in my experience with Churches, is very attractive. AWS
charges based on your usage, no matter how much you use. With Heroku, we can spin
up what's called a 'dyno' (a light-weight Linux container that runs application
code) with a fixed cost. For those interested parties, at the time of writing,
the cost of a Hobby Heroku dyno is $7 a month (but it will be less than this as
you use it less.) Some churches will be able to get away with Heroku's free tier
which means the cost is $0. Secondly, the service is *easy* to use, which means
the person reading this doc will hopefully have a much easier time setting up
the service, and then it's pretty much set-and-forget. Thirdly and finally, it's
also got an excellent integration with Github (and it's own internal Git service
which is even easier, but not what we'll use here) that means a push to the configured
branch will automatically be deployed, so making changes is really nice and easy.
It's also very intuitive!

If you are an AWS expert, and you still want to use it, that's okay too. I won't
bore you with the setup for Elastic Beanstalk on AWS, the 'Elasticloud' key/val
memory store you'll need, or even the database config on RDS which you'll need
to set up, but it's a great blessing for your church that you're willing to be
dilligent and save the church some money every month! I can't guarantee that this
project will work without needing some adjustment in the `src/models/db.py` file
to get everything working, but I suspect you can figure it out :)

**A quick note:** we'll still be using S3 for storage, so we aren't totally
abandoning Jeff Bezos's galactic empire.

#### Setting up with Heroku
Okay, for those of you who **do** want to use Heroku, here's the guide:

1. Set up an account, and add your card details (no money will be taken).
2. Download the Heroku CLI and then install it on your local machine
3. Go to the Heroku Dashboard > Create New Pipeline
4. Add a sensible pipeline name
5. Connect your GitHub profile and then search for and select the forked
project.
6. Create it.
7. Add an app in the 'staging' section > create new app > choose the same name,
probably > pick a region and then > create.
8. Find your app, and add the 'add-ons' 'heroku-postgres' and 'heroku-redis'
(it should be in overview page > configure add-ons)

**Note:** Now, the system should recognise the new credentials on start-up and use them,
so there isn't anything else to configure there.

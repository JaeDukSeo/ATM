ATM - Auto Tune Models
====
Docs available here: https://hdi-project.github.io/ATM/intro.html

ATM is an open source software library under ["The human data interaction project"](https://hdi-dai.lids.mit.edu/) at MIT.  It is a distributed scalable AutoML system designed with ease of use in mind. ATM takes in data with pre-extracted feature vectors and labels (target column) in a simple CSV file format. It attempts to learn several classifiers (machine learning models to predict the label) in parallel. In the end, ATM returns a number of classifiers and the best classifier with a specified set of hyperparameters. 

## Current status
**atm** and the accompanying library **btb** are under active development (transitioning from an older system to a new one). In the next couple of weeks we intend to update its documentation, its testing infrastructure, provide APIs and establish a framework for the community to contribute. Stay tuned for updates. Meanwhile, if you have any questions or you would like to receive updates, **please email dailabmit@gmail.com. **

## Setup/Installation 
This section describes the quickest way to get started with ATM on a modern
machine running Ubuntu Linux. We hope to have more in-depth guides in the
future, but for now, you should be able to substitute commands for the package
manager of your choice to get ATM up and running on most modern Unix-based
systems.

1. **Clone the project**.
   ```
      $ git clone https://github.com/hdi-project/atm.git /path/to/atm
      $ cd /path/to/atm
   ```

2. **Install a database.**
   - for SQLite (simpler):
   ```
      $ sudo apt install sqlite3
   ```

   - for MySQL: 
   ```
      $ sudo apt install mysql-server mysql-client
   ```

3. **Install python dependencies.**
   ```
      $ virtualenv venv
      $ . venv/bin/activate
      $ pip install -r requirements.txt
   ```
   This will also install [btb](https://github.com/hdi-project/btb), the core AutoML library in development under the HDI project, as an egg which will track changes to the git repository.

## Quick Usage
Below we will give a quick tutorial of how to run atm on your desktop. We will use a featurized dataset, already saved in ``data/test/pollution_1.csv``. This is one of the datasets available on [openml.org](https://www.openml.org). More details can be found [here](https://www.openml.org/d/542). In this problem the goal is predict ``mortality`` using the metrics associated with the air pollution. Below we show a snapshot of the ``csv`` file.  The data has 15 features and the last column is the ``class`` label. 

  |PREC | JANT |  JULT |  OVR65 |	POPN|	EDUC|	HOUS| DENS|	NONW|	WWDRK	|POOR| HC	| NOX |	SO@	| HUMID |	class|
  |:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
   |35	|   23	|   72	|   11.1	|   3.14	|  11	|  78.8	|   4281	|  3.5	|50.7	|14.4	|8	|   10	|   39	|   57	|      1|
   |44	|   29	|   74	|   10.4|	   3.21	 | 9.8	|  81.6	|   4260	|  0.8|	39.4|	12.4	|6	|   6	 |  33	|   54	|      1|
   |47	|   45	|   79	|   6.5	 |  3.41	| 11.1	|77.5	 |  3125	|  27.1	|50.2|	20.6|	18	 |  8	 |  24|	   56	 |     1|
   |43	|   35|	   77	 |  7.6	 |  3.44	|  9.6	|  84.6	|   6441	|  24.4	|43.7	|14.3	|43	|   38|	   206|	55	|      1|
   |53	|   45	|   80	|   7.7	|   3.45|	  10.2|	66.8	|   3325|	  38.5	|43.1|	25.5|	30	|   32|	   72	 |  54	|      1|
  | 43	|   30	|   74	|   10.9|	   3.23	|  12.1|	83.9|	   4679|	  3.5	|49.2	|11.3	|21	|   32|	   62	|   56	|      0|
   |45	|   30	|   73	|   9.3	|   3.29	|  10.6	|86	 |    2140	|  5.3|	40.4	|10.5|	6	|   4	|   4	|   56|	      0|
  | ..	|   ..	|   ..	|   ...	|   ....|	  ....	|...	|     ....	|  .. |	....|	....|	..	|   ..|    ..	|   ..|	      .|
 |  ..	|   ..|	   ..	|   ...	|   ....	|  ....	|...|	     ....	 | .. 	|....	|....|	..|	   .. |   ..|	   ..	 |     .|
  |..|	   ..	|   ..	|   ...|	   ....|	  ....|	...	|     ....	|  ..| 	....|	....|	..	|   .. |   ..|	   ..	 |     .|
  | 37	|   31|	   75	 |  8	 |    3.26|	11.9	|78.4	 |    4259|	  13.1	|49.6|	13.9|	23	|   9	|   15|	   58	 |    1|
  | 35	|   46|	   85	 |  7.1	 |  3.22|	  11.8	|79.9	|   1441	|  14.8	|51.2	|16.1|	1	|   1	 |  1	|   54	|      0|

   
1. **Create a datarun** 
    ```
      $ python atm/enter_data.py
    ```
   This command will create a ``Datarun``. A ``Datarun`` in ATM is a single logical machine learning task. If you run the above command without any arguments, it will use the following default settings:
   * ``sqllite`` as the database 
   * ``atm.db`` as the database name (more about what is collected in this database and what is it used for is described [here](https://cyphe.rs/static/atm.pdf)
   * ``pollution_1.csv`` as the dataset for which classifiers are sought. 
   * it will use the settings specified in ``run_config.yaml`` for btb (which is the tuning library)
   
   The command should produce a lot of output, the end of which looks something like this:
  
    ```
        ========== Summary ==========
        Training data: data/test/pollution_1.csv
        Test data: <None>
        Dataset ID: 1
        Frozen set selection strategy: uniform
        Parameter tuning strategy: gp_ei
        Budget: 100 (learner)
        Datarun ID: 1
    ```

   The most important piece of information is the datarun ID.
 
 
2. **Start a worker**
     ```
        $ python atm/worker.py 
     ```

   This will start a process that computes learners (classifiers) and saves them to the model
   directory. The output should show which hyperparameters are being tested and the performance of
   each learner (the "judgment metric"), plus the best overall performance so far.
   ```
    Classifier type: classify_logreg
    Params chosen:
            C = 8904.06127554
            _scale = True
            fit_intercept = False
            penalty = l2
            tol = 4.60893080631
            dual = True
            class_weight = auto

    Judgment metric (f1): 0.536 +- 0.067
    Best so far (learner 21): 0.716 +- 0.035
   ```
   Occassionally the worker will throw an error when it can't learn a classifier due to erroneous settings. The errors are logged in the database. The worker however moves on to trying the next classifier.  

You can break out of the worker with Ctrl+C and restart it with the same command; it will pick up right where it left off. You can also start multiple workers at the same time in different   terminals to parallelize the work by calling the above command again. When all 100 learners in your budget have been computed, all workers will exit gracefully.
 
## Customizing config settings, and running on your own data 

ATM has the following features:
* It allows users to simulataneously run the system for multiple datasets 
* Users can run on AWS or a cluster compute 
* It makes use of a variety of AutoML approaches for tuning and selection available in the accompanying library [btb]()
* It stores models, metrics and cross validated accuracy information about each classifier it learnt. 
There are a number of ways user can use the system and most of it is controlled through the three yaml files in ``conig/templates/``. Our documentation will cover all these scenarios and settings. 

1. **Running for your own dataset** 
   If you want to use the system for your own dataset, create a csv file similar to the example shown above. The format is:
   * Each column is a feature 
   * Each row is a training example 
   * The last column in the target column and is called ``class``
   * The first row is the header row. 
   
    
2. **Create copies of the sample configuration files, and edit them to
   add your settings.** 

      Saving configuration as YAML files is an easy way to save complicated setups or
      share them with team members. However, if you want, you can skip this step and
      specify all configuration parameters on the command line later.

      If you do want to use YAML config files, you should start with the templates
      provided in `config/templates` and modify them to suit your own needs.
      ```
         $ cp config/templates/*.yaml config/
         $ vim config/*.yaml
      ```

      `run_config.yaml` contains all the settings for a single Dataset and Datarun.
      Specify the `train_path` to point to your own dataset.

      `sql_config.yaml` contains the settings for the ModelHub SQL database. The
      default configuration will connect to (and create if necessary) a SQLite
      database called atm.db. If you are using a MySQL database, you will need to
      change it to something like this: 
      ```
         dialect: mysql
         database: atm
         username: username
         password: password
         host: localhost
         port: 3306
         query:
      ```

      If you need to download data from an Amazon S3 bucket, you should update
      `aws_config.yaml` with your credentials.

3. **Create a datarun.**
   ```
      $ python atm/enter_data.py --command --line --args
   ```

   This command will create a Datarun and a Dataset (if necessary) and store both
   in the ModelHub database. If you have specified everything in .yaml config
   files, you should call it like this:

   ```
      $ python atm/enter_data.py --sql-config config/sql_config.yaml \
      --aws-config config/aws_config.yaml \
      --run-config config/run_config.yaml
   ```

   Otherwise, the script will use the default configuration values (specified in
   atm/config.py), except where overridden by command line arguments. You can also
   use a mixture of config files and command line args; any command line arguments
   you specify will override the values found in config files.

  

4. **Start a worker, specifying your config files and the datarun(s) you'd like to
   compute on.**
   ```
      $ python atm/worker.py --sql-config config/sql_config.yaml \
      --aws-config config/aws_config.yaml --dataruns 1
   ```

   This will start a process that computes learners and saves them to the model
   directory you configured. If you don't specify any
   dataruns, the worker will periodically check the ModelHub database for new
   dataruns, and compute learners for any it finds in order of priority.  The
   output should show which hyperparameters are being tested and the performance of
   each learner (the "judgment metric"), plus the best overall performance so far.
   ```
    Classifier type: classify_logreg
    Params chosen:
            C = 8904.06127554
            _scale = True
            fit_intercept = False
            penalty = l2
            tol = 4.60893080631
            dual = True
            class_weight = auto

    Judgment metric (f1): 0.536 +- 0.067
    Best so far (learner 21): 0.716 +- 0.035
   ```
   And that's it! You can break out of the worker with Ctrl+C and restart it with
   the same command; it will pick up right where it left off. You can also start
   multiple workers at the same time in different terminals to parallelize the
   work. When all 100 learners in your budget have been computed, all workers will
   exit gracefully.

<!--## Testing Tuners and Selectors-->

<!--The script `test_btb.py`, in the main directory, allows you to test different-->
<!--BTB Tuners and Selectors using ATM. You will need AWS access keys from DAI lab-->
<!--in order to download data from the S3 bucket. To use the script, -->
<!--config file as described above, then add the following fields (replacing the-->
<!--API keys with your own):-->

<!--```-->
<!--[aws]-->
<!--access_key: YOURACCESSKEY-->
<!--secret_key: YoUrSECr3tKeY-->
<!--s3_bucket: mit-dai-delphi-datastore-->
<!--s3_folder: downloaded-->
<!--```-->

<!--Then, add the name of the data file you want to test:-->

<!--```-->
<!--[data]-->
<!--alldatapath: filename.csv-->
<!--```-->

<!--To test a custom implementation of a BTB tuner or selector, define a new class called:-->
  <!--* for Tuners, CustomTuner (inheriting from btb.tuning.Tuner)-->
  <!--* for Selectors, CustomSelector (inheriting from btb.selection.Selector)-->
<!--You can see examples of custom implementations in-->
<!--btb/selection/custom\_selector.py and btb/tuning/custom\_tuning.py. Then, run-->
<!--the script:-->

<!--```-->
<!--python test_btb.py --config config/atm.cnf --tuner /path/to/custom_tuner.py --selector /path/to/custom_selector.py-->
<!--```-->

<!--This will create a new datarun and start a worker to run it to completion. You-->
<!--can also choose to use the default tuners and selectors included with BTB:-->

<!--```-->
<!--python test_btb.py --config config/atm.cnf --tuner gp --selector ucb1-->
<!--```-->

<!--Note: Any dataset with less than 30 samples will fail for the DBN classifier unless the DBN `minibatch_size` constant is changed to match the number of samples.-->

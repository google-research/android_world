# AndroidWorld

**AndroidWorld** is an environment for building autonomous computer control agents.

It runs on a live Android emulator, consisting of a highly reproducible task suite with 116 hand-crafted tasks across 20 apps, which are dynamically instantiated with randomly-generated parameters to create millions of unique task variations.

In addition to the built-in tasks, AndroidWorld also supports the popular web benchmark, MiniWoB++ from [Liu et al.](http://arxiv.org/abs/1802.08802).

Key features of AndroidWorld include:

* Open environment with access to millions of Android apps and websites
* 116 diverse tasks across 20 real-world apps
* Dynamic task instantiation for millions of unique variations
* Durable reward signals for reliable evaluation
* Lightweight footprint (2 GB memory, 8 GB disk)
* Extensible design to easily add new tasks and benchmarks
* Integration with MiniWoB++ web-based tasks

Watch a demo of an agent interacting with AndroidWorld [here](todo).

## Installation

1. Set up the Android Emulator
 1. Download Android Studio [here](https://developer.android.com/studio?gad_source=1&gclid=Cj0KCQjw3ZayBhDRARIsAPWzx8oLcadBD0vAq8xmUutaunLGSzhgEtLz4xVZ_SpV4G0xJazS7LxQkDsaAuveEALw_wcB&gclsrc=aw.ds)
 2. Create an Android Virtual Device (AVD) by following these instructions. For hardware select **Pixel 6**, for System Image select **Tiramisu, API Level 33**, and choose AVD name as **AndroidWorldAvd**.

2. Launch the Android Emulator from the command line

  ```bash
  # Typically it's located in ~/Android/Sdk/emulator/emulator or
  # ~/Library/Android/sdk/emulator/emulator
  EMULATOR_NAME=AndroidWorldAvd # From previous step
  ~/Library/Android/sdk/emulator/emulator -avd $EMULATOR_NAME -no-snapshot -grpc 8554
  ```

1. Install the latest [AndroidEnv](https://github.com/google-deepmind/android_env):

  ```python
  git clone https://github.com/google_deepmind/android_env
  cd android_env
  python setup.py install
  ```

3. Install AndroidWorld

 [Optional] It's recommended to use `conda`, which you can download [here](https://docs.anaconda.com/free/miniconda/miniconda-install/).

  ```
  conda create -n android_world python=3.11.8
  conda activate android_world
  ```
  Install AndroidWorld:

  ```python
  git clone https://github.com/google-research/android_world.git
  cd ./android_world
  python setup.py install
  ```

4. Add model provider APIs as environment variables.

  ```bash
  # Add to .bashrc.
  export OPENAI_API_KEY=your-key
  export GCP_API_KEY=your-key
  ```


## Run the benchmark

```bash
python run.py \
  --suite_family=android_world \
  --agent_name=t3a \
  --tasks=ClockStopWatchPausedVerify  # Just run on one task for testing.
  --perform_emulator_setup \  # First time only.
```

The first time you run this script, you must install the necessary apps and set permissions by specifying `--perform_emulator_setup`. This is a one-time setup.

The `n_task_combinations` argument specifies how many parameter permutations to use for each task. For example, for an SMS task, it would correspond to different phone number/message combinations for each run.

You can specify an optional `--tasks` flag to run on a subset of tasks.

If a run fails partway through, you can resume it by re-running the script with the `--checkpoint_dir` flag pointing to the output directory from the original run.

TODO: Please see tasks.txt for a full list of available tasks.

## Running MiniWoB++ tasks

To run the MiniWoB++ web-based tasks in AndroidWorld, simply set
`--suite_family=miniwob` in the command above.

A key advantage of running MiniWoB++ tasks is that common input elements are
rendered as native, commonly used Android UI widgets, rather than as HTML. Thus agents must learn to use universal
widgets such as time- and date-pickers:

![Android Widget](imgs/miniwob.png){style="display:block;margin:auto; width:10rem;"}


*This is not an officially supported Google product.*

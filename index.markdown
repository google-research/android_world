---
permalink: /
layout: home
title: AndroidWorld
---

<div align="center">
<p align="center" style="font-size:20px">
Chris Rawles<sup  style="font-size:10px">1</sup>, Yifan Chang<sup style="font-size:10px">2</sup>, Sarah Clinckemaillie<sup style="font-size:10px">2</sup>, Jonathan Waltz<sup style="font-size:10px">2</sup>, Gabrielle Lau<sup style="font-size:10px">2</sup>, Marybeth Fair<sup style="font-size:10px">2</sup>, Robert Berry<sup style="font-size:10px">1</sup>, Wei Li<sup style="font-size:10px">1</sup>, Will Bishop<sup style="font-size:10px">1</sup>, Alice Li<sup style="font-size:10px">1</sup>, Folawiyo Campbell-Ajala<sup style="font-size:10px">1</sup>, Divya Tyam<sup style="font-size:10px">2</sup>, Daniel Toyama<sup style="font-size:10px">1</sup>, Timothy Lillicrap<sup style="font-size:10px">1</sup>, Oriana Riva<sup style="font-size:10px">1</sup>
</p>
<p align="center" style="font-size:20px">
<sup style="font-size:10px">1 </sup>Google DeepMind
<sup style="font-size:10px">2 </sup>Google Research
</p>
<p align="center">
<a href=""><b>Paper</b></a> •
<a href="https://github.com/google-research/android_world"><b>Code</b></a> •
<a href="https://github.com/google-research/android_world/blob/main/android_world/task_metadata.json"><b>Data</b></a>
</p>

</div>
<br>
<div class="video-row">
  <div class="video-content">
    <video height='80%' width='80%' autoplay muted loop playsinline controls>
      <source src="assets/videos/AudioRecorderRecordAudioWithFileName.mp4" type="video/mp4">
    </video>
    <div class="overlay">
      <p>(a) Record an audio and save it</p>
    </div>
  </div>
  <div class="video-content">
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/ExpenseAddMultiple.mp4" type="video/mp4">
    </video>
    <div class="overlay">
      <p>(b) Add multiple expenses.</p>
    </div>
  </div>
  <div class="video-content">
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/OsmAndMarker.mp4" type="video/mp4">
    </video>
    <div class="overlay">
      <p>(c) Create a marker in a map app</p>
    </div>
  </div>
</div>
<div class="video-row">
  <div class="video-content">
    <video height='80%' width='80%' autoplay muted loop playsinline controls>
      <source src="assets/videos/RecipeAddMultipleRecipes.mp4" type="video/mp4">
    </video>
    <div class="overlay">
      <p>(d) Create multiple recipes.</p>
    </div>
  </div>
  <div class="video-content">
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/SimpleCalendarAddOneEventRelativeDay-Fail.mp4" type="video/mp4">
    </video>
    <div class="overlay">
      <p>(e) Add a calendar event.</p>
    </div>
  </div>
    <div class="video-content">
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/VlcCreatePlaylist_2x.mp4" type="video/mp4">
    </video>
    <div class="overlay">
      <p>(f) Create a playlist in VLC.</p>
    </div>
  </div>
</div>
<div class="video-row">
  <div class="video-content">
    <video height='80%' width='80%' autoplay muted loop playsinline controls>
      <source src="assets/videos/SimpleSmsSendReceivedAddress.mp4" type="video/mp4">
    </video>
    <div class="overlay">
      <p>(g) Send received address to contact.</p>
    </div>
  </div>
  <div class="video-content">
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/TasksHighPriorityTasksDueOnDate_2x.mp4" type="video/mp4">
    </video>
    <div class="overlay">
      <p>(h) Retrieve high priority tasks due on date.</p>
    </div>
  </div>
  <div class="video-content">
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/SportsTrackerTotalDistanceForCategoryOverInterval_2x.mp4" type="video/mp4">
    </video>
    <div class="overlay">
      <p>(i) Retrieve sports tracking stats.</p>
    </div>
  </div>
</div>


## Abstract
{% include_relative abstract.md %}

## Dataset
Key Features:
* 📝 116 diverse tasks across 20 real-world apps
*  🎲 Dynamic task instantiation for millions of unique variations
*  🏆 Durable reward signals for reliable evaluation
*  🌐 Open environment with access to millions of Android apps and websites
*  💾 Lightweight footprint (2 GB memory, 8 GB disk)
*  🔧 Extensible design to easily add new tasks and benchmarks
 * 🖥️ Integration with MiniWoB++ web-based tasks

### Dataset Statistics

<div class="dataset-graphs" style="display:flex">
  <div style="width:50%">
   <img src="assets/images/tagcounts.png" alt="Task tags distribution" >
    <p style="text-align:center"> The distribution tags across AndroidWorld tasks </p>
    </div>
  <div class="steps-graph" style="width:50%">
    <img src="assets/images/stepscounts.png" alt="Task step histogram">
    <p style="text-align:center"> The distribution of the number of steps taken to perform tasks </p>
  </div>
</div>



### Comparison to other datasets
<img src="assets/images/dataset_comparison.png" alt="Table comparing AndroidWorld to other datasets">


## Paper
AndroidWorld is described in [http://arxiv.org/TODO](our publication (PDF)).

## Run Benchmark
See our <a href="https://github.com/google-research/android_world">github repository</a> for instructions on running the benchmark.

## Citation
<pre>
@misc{androidworld,
  title={AndroidWorld: A Dynamic Benchmarking Environment for Autonomous Agents},
  author={Chris Rawles and Yifan Chang and Sarah Clinckemaillie and Jonathan Waltz and Gabrielle Lau and Marybeth Fair and Robert Berry and Wei Li and Will Bishop and Alice Li and Folawiyo Campbell-Ajala and Divya Tyam and Daniel Toyama and Timothy Lillicrap and Oriana Riva},
  archivePrefix={arXiv},
  eprint={},
  year={2024}
}
</pre>



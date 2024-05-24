---
permalink: /
layout: home
title: "AndroidWorld: A Dynamic Benchmarking Environment for Autonomous Agents"
---

<div align="center">
<style>
  .rounded-button {
  border-radius: 290486px;
  padding-left: 1.25em;
  padding-right: 1.25em;
  padding-top: 10px;
  padding-bottom: 10px;
  background-color: #151313;
  border-color: transparent;
  color: #fff;
}
a.rounded-button, a.rounded-button:visited, a.rounded-button:hover, a.rounded-button:active {
  color: #fff;
}
  
span.icon {
    padding-right: 10px;
}
  </style>
<p align="center" style="font-size:20px">
Chris Rawles<sup  style="font-size:10px">*1</sup>, Yifan Chang<sup style="font-size:10px">†2</sup>, Sarah Clinckemaillie<sup style="font-size:10px">†2</sup>, Jonathan Waltz<sup style="font-size:10px">2</sup>, Gabrielle Lau<sup style="font-size:10px">2</sup>, Marybeth Fair<sup style="font-size:10px">2</sup>, Robert Berry<sup style="font-size:10px">1</sup>, Wei Li<sup style="font-size:10px">1</sup>, Will Bishop<sup style="font-size:10px">1</sup>, Alice Li<sup style="font-size:10px">1</sup>, Folawiyo Campbell-Ajala<sup style="font-size:10px">1</sup>, Divya Tyamagundlu<sup style="font-size:10px">2</sup>, Daniel Toyama<sup style="font-size:10px">1</sup>, Timothy Lillicrap<sup style="font-size:10px">1</sup>, Oriana Riva<sup style="font-size:10px">1</sup>
</p>
<p align="center" style="font-size:16px">
<sup style="font-size:10px">1 </sup>Google DeepMind
<sup style="font-size:10px">2 </sup>Google
<br>
<sup style="font-size:10px">*</sup>Lead contributor
<sup style="font-size:10px"> †</sup>Equal contribution 
</p>
<p align="center">
<a class="rounded-button" href="https://arxiv.org/pdf/2405.14573"><span class="icon"><i class="ai ai-arxiv"></i></span><span>Paper</span></a>
<a class="rounded-button" href="https://github.com/google-research/android_world"><span class="icon"><i class="fa-brands fa-github"></i></span><span>Code</span></a>
<a class="rounded-button" href="https://github.com/google-research/android_world/blob/main/android_world/task_metadata.json"><span class="icon"><i class="fa-regular fa-images"></i></span><span>Data</span></a>
</p>

<img src="assets/images/aw_graph.png" alt="Overview of AndroidWorld ">

{% include_relative abstract.md %}

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

## Citation
<pre>
@misc{rawles2024androidworld,
      title={AndroidWorld: A Dynamic Benchmarking Environment for Autonomous Agents}, 
      author={Christopher Rawles and Sarah Clinckemaillie and Yifan Chang and Jonathan Waltz and Gabrielle Lau and Marybeth Fair and Alice Li and William Bishop and Wei Li and Folawiyo Campbell-Ajala and Daniel Toyama and Robert Berry and Divya Tyamagundlu and Timothy Lillicrap and Oriana Riva},
      year={2024},
      eprint={2405.14573},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
</pre>



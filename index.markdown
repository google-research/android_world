---
permalink: /
layout: home
title: AndroidWorld
---

<div align="center">
<p align="center" style="font-size:20px">
Chris Rawles, Yifan Chang, Sarah Clinckemaillie, Jonathan Waltz, Gabrielle Lau, Robert Berry, Wei Li, Will Bishop, Alice Li, Folawiyo Campbell-Ajala, Divya Tyam, Daniel Toyama, Timothy Lillicrap, Oriana Riva
</p>
<p align="center">
<a href="#dataset"><b>Dataset</b></a> •
<a href=""><b>Paper</b></a> •
<a href="#download-data"><b>Download Data</b></a> •
<a href="#license--contact"><b>License & Contact</b></a>
</p>

</div>

## Abstract
{% include_relative abstract.md %}


## Dataset
Key Features:
 - 116 manually created tasks across 20 open source apps.
 - Benchmark is using a real world environment running on an Android emulator.
 - All tasks are parametrized, adding variety and making it more difficult for agents to just memorize each task.
 - Task success is determined by the outcome state, and is thus independent of the path the agent took to complete it.
 - Tasks assess an agent across a wide variety of agent capabilities and task complexity.
 - Includes both tasks that change the device state and information retrieval tasks.

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

### Dataset Contents
These tasks span a broad spectrum of app domains, below are a few examples:

<div class="video-row">
  <div class="video-content">
    <div class="overlay">
      <p>(a) Record an audio and save it</p>
    </div>
    <video height='80%' width='80%' autoplay muted loop playsinline controls>
      <source src="assets/videos/AudioRecorderRecordAudioWithFileName.mp4" type="video/mp4">
    </video>
  </div>
  <div class="video-content">
    <div class="overlay">
      <p>(b) Add multiple expenses.</p>
    </div>
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/ExpenseAddMultiple.mp4" type="video/mp4">
    </video>
  </div>
  <div class="video-content">
    <div class="overlay">
      <p>(c) Create a marker in a map app</p>
    </div>
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/OsmAndMarker.mp4" type="video/mp4">
    </video>
  </div>
</div>
<div class="video-row">
  <div class="video-content">
    <div class="overlay">
      <p>(e) Create multiple recipes.</p>
    </div>
    <video height='80%' width='80%' autoplay muted loop playsinline controls>
      <source src="assets/videos/RecipeAddMultipleRecipes.mp4" type="video/mp4">
    </video>
  </div>
  <div class="video-content">
    <div class="overlay">
      <p>(f) Add a calendar event.</p>
    </div>
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/SimpleCalendarAddOneEventRelativeDay-Fail.mp4" type="video/mp4">
    </video>
  </div>
    <div class="video-content">
    <div class="overlay">
      <p>(g) Create a playlist in VLC.</p>
    </div>
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/VlcCreatePlaylist_2x.mp4" type="video/mp4">
    </video>
  </div>
</div>
<div class="video-row">
  <div class="video-content">
    <div class="overlay">
      <p>(h) Send received address to contact.</p>
    </div>
    <video height='80%' width='80%' autoplay muted loop playsinline controls>
      <source src="assets/videos/SimpleSmsSendReceivedAddress.mp4" type="video/mp4">
    </video>
  </div>
  <div class="video-content">
    <div class="overlay">
      <p>(i) Retrieve high priority tasks due on date.</p>
    </div>
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/TasksHighPriorityTasksDueOnDate_2x.mp4" type="video/mp4">
    </video>
  </div>
  <div class="video-content">
    <div class="overlay">
      <p>(j) Retrieve sports tracking stats.</p>
    </div>
    <video height='80%' width='80%' class="video" controls autoplay playsinline muted loop>
      <source src="assets/videos/SportsTrackerTotalDistanceForCategoryOverInterval_2x.mp4" type="video/mp4">
    </video>
  </div>
</div>


## Paper
AndroidWorld is described in [http://arxiv.org/TODO](our publication (PDF)).

## Download Data
See our <a href="https://github.com/google-research/android_world">github repository</a> for instructions on downloading data.

## License & Contact



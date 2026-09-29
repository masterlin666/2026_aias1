// Module 7 Lab - Chisel Basics
val chiselVersion = "3.5.6"

lazy val root = (project in file("."))
  .settings(
    name := "module7-lab",
    scalaVersion := "2.13.10",
    libraryDependencies ++= Seq(
      "edu.berkeley.cs" %% "chisel3" % chiselVersion,
      "edu.berkeley.cs" %% "chiseltest" % "0.5.6" % "test",
      "edu.berkeley.cs" %% "chisel-iotesters" % "2.5.6",
    ),
    scalacOptions ++= Seq(
      "-language:reflectiveCalls",
      "-deprecation",
      "-feature",
      "-Xcheckinit",
    ),
    addCompilerPlugin("edu.berkeley.cs" %% "chisel3-plugin" % chiselVersion cross CrossVersion.full),
  )

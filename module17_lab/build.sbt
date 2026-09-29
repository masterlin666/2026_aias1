// Module 17 Lab - Chisel project
val chiselVersion = "3.6.1"

lazy val root = (project in file("."))
  .settings(
    name := "module17-lab",
    scalaVersion := "2.13.14",
    libraryDependencies ++= Seq(
      "edu.berkeley.cs" %% "chisel3" % chiselVersion,
      "edu.berkeley.cs" %% "chiseltest" % "0.6.2" % "test",
    ),
    scalacOptions ++= Seq(
      "-language:reflectiveCalls",
      "-deprecation",
      "-feature",
      "-Xcheckinit",
    ),
    addCompilerPlugin("edu.berkeley.cs" %% "chisel3-plugin" % chiselVersion cross CrossVersion.full),
  )

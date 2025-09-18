# Ariadne

A small utility to find your way through complex JSON objects by providing an example.

## The Problem

When interacting with APIs, you often get back large, deeply-nested JSON responses. Finding the correct path to the specific data you need can feel like navigating a labyrinth.

## The Solution

`ariadne` simplifies this. You provide:
1.  A "control" JSON file (the original, full response).
2.  An "annotated" JSON file (a copy where you've replaced the data you want with a placeholder tag).

The tool then compares the two, finds your placeholders, and generates simple Python helper functions to access that data, giving you a thread to follow through the labyrinth.

## Installation

```bash
pip install .
```

## Usage

```bash
ariadne control.json annotated.json
ariadne control.json annotated.json -o helpers.py
```

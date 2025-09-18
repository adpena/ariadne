# JSON by Example (`jxbe`)

A small utility to find paths in complex JSON objects by providing an example.

## The Problem

When interacting with APIs, you often get back large, deeply-nested JSON responses. Finding the correct path to the specific data you need can be a tedious process of trial and error.

## The Solution

`json-by-example` simplifies this. You provide:
1.  A "control" JSON file (the original, full response).
2.  An "annotated" JSON file (a copy where you've replaced the data you want with a placeholder tag).

The tool then compares the two, finds your placeholders, and generates simple Python helper functions to access that data.

## Installation

```bash
pip install .
```

## Usage

```bash
jxbe control.json annotated.json
```

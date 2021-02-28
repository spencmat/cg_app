# cg_app
Content Generator Service for OSU CS361

## Requirements
Beautiful Soup and Requests libraries are required to run the Content Generator. Install them from the requirements.txt file:
```
pip install -r requirements.txt
```

## Running Content Generator

To use the GUI: 
```
python content-generator.py
```

To use the CLI:
```
python content-generator.py input.csv 
```

## Running Content Generator with Life Generator Service 

To use the Life Content Generator (Integration with Life Generator service), you will need to specify the `--life-content-generator` parameter. `life-generator.py` and its requirements need to be in the same directory.
```
python content-generator.py --life-content-generator
```

If life-generator.py is in a different directory, you can specify the location.
```
python content-generator.py --life-content-generator=/Users/spencer/Documents/lg_app
```

See `input_example.csv` and `output_example.csv` for formatting examples.


<embed type="video/webm" src="images/content-generator-recording.mov"/>

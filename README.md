## About
This is a script that will generate and overlay a minimap of the photos location. \
This is the given example
![Malta](output/Example_overlay.png)

## Install
Clone this repository and install the necessary packages using
```
pip install -r requirements.txt
```
## Usage
Simply call it and pass the photos directory or a single photo.
```
python bedwarsshop.py username
```
If you cloned this repo you can try out the example
```
python main.py ".\test\Example.jpg"  --trip_route .\test\example.csv
```
You can always run the help command
```
python main.py --help
```
For more customizations check out constants.py file. For adjusting colors, thicknesses or adding more icon support.


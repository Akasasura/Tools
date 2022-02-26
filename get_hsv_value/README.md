# get_hsv_value

## this tool is used to get HSV value from an image for an object detection based on color

## TODO:

- [x] get HSV value with clicking the `img` window
- [x] get HSV value with slider
- [x] get HSV value with selecting ROI by pressing `R` in runtime
- [x] saving the value with json format inside `color.json`
- [x] load the saved value
- [x] add camera capture, so doesn't need to prepare the image first XD
- [x] get HSV lower and upper value based on the min and max value from other pixel in the radius x from the clicked one
- [x] save saved color to desired directory
- [x] load video
- [ ] seperate HSV slider from HSV window and make GUI for saving, loading object, and exit from loop
- [ ]
<hr>

## How to Use

- to see arguments run with

```bash
python get_hsv_value.py --help
```

- to use image instead of camera it needs positional arguments of your image path from your current working directory

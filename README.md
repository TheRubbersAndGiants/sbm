# sbm
sbm stands for Sunlit Bitmap and is a bitmap file type that can be written by hand using code.

## Usage
To use this you must first download the lastest release and run sbminstall.bat to install sbm. After installation you can make a folder named whatever and put a file named '.txt' inside, it has to be named '.txt' to work when being converted to a .sbm file. the header must be sbm(horizontalsize)! replace horizontalsize with the horizontal length of the image you are making. When you are making an image you can use presets ('r':
'Red', 'o': 'Orange', 'y': 'Yellow', 'g': 'Green', 't': 'Teal', 'u': 'Navy', 'i': 'Indigo', 'v': 'Violet', 'p': 'Purple', 'h': 'Brown', 'l': 'Black', 'w': 'White', 'x': 'Transparent') you can also remove and add RGB to the presets like r+g22 to add 22 green to red. You may also input pure RGBA hex values. A special preset is 's' letting you use a file in the same directory as .txt named 'hex.txt' containing the RGBA hex code of your desired custom preset. This is stored inside of the SBM file meaning every image can have its own custom preset.

## Examples
Examples for a single pixel would be `sbm1!r+g22` which is a red pixel with 22 green value and would be #ff1600 or rgba(255, 22, 0, 1). More examples are `sbm4!r,g,r,g,r,g,r,g,r,g,r,g,r,g,r,g` to get pattern of red and green.

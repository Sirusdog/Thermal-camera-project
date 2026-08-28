#include "opencv2/core.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/videoio.hpp"
#include <raylib-cpp.hpp>
#include <iostream>
#include <stdio.h>

#ifndef CAMERA_CONTROLLER_H
#define CAMERA_CONTROLLER_H

using namespace cv;
using namespace std;

class CameraController {
    private:
        VideoCapture cap;

        int deviceID;
        int apiID;

        int xSize, ySize; // Scaled cam size

        float rPal, gPal, bPal, brightness, scale; // Pallet modifiers
        int mode; // Mode selection
        volatile bool locked; // Is locked? for protecting frame.

    public:
        volatile bool isRunning;
        Image frame;
        Image lastFrame;

    private:
        void captureLoop();

    public:
        CameraController(int x, int y);
        Image getFrame();
        void startCaptureLoop();
        void stopCaptureLoop();
        void setScale(float newScale);
};


#endif
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <stdio.h>
#include <thread>
#include "CameraController.hpp"

using namespace std;
using namespace cv;

CameraController::CameraController(int x, int y){
    isRunning = true;
    locked = false;
    deviceID = 0;
    apiID = cv::CAP_ANY;
    xSize = x;
    ySize = y;
    rPal = 1.0;
    gPal = 1.0;
    bPal = 1.0;
    brightness = 1.0;
    scale = 1.0;
    mode = 0;
};


void CameraController::captureLoop() {
    // Opens the capture
    cap.open(deviceID, apiID);

    if (!cap.isOpened()) {
        cerr << "Camera failed to open, exiting.\n";
        return;
    }

    Mat rawFrame;
    Mat greyFrame;
    Mat blur;

    while (isRunning) {
        // Continuously reads in frames.
        locked = true;
        cap.read(rawFrame);
        if (rawFrame.empty()) {
            cout << "Capture not found!" << endl;
        }
        // Mode 0 = Direct camera output.
        // Mode 1 = Edge detection mode
        // Mode 2 = 
        switch (mode) {
            case 0:
                cvtColor(rawFrame, frame, cv::COLOR_BGR2RGB);
            case 1:
                cvtColor(rawFrame, greyFrame, cv::COLOR_BGR2GRAY);

                GaussianBlur(greyFrame, blur, cv::Size(5, 5), 1.4);
            
                Canny(blur, frame, 100, 200);
            default:
                cvtColor(rawFrame, frame, cv::COLOR_BGR2RGB);
        }
        resize(frame, frame, cv::Size(xSize, ySize));
        locked = false;
    }
    return;
};

void CameraController::startCaptureLoop() {
    thread capThread(&CameraController::captureLoop, this);
}

void CameraController::stopCaptureLoop() {
    isRunning = false;
}

Mat CameraController::getFrame() {
    while (locked) {}
    return frame;
};

void CameraController::setScale(float newScale) {
    xSize = static_cast <int>(round(xSize * newScale));
    ySize = static_cast <int>(round(xSize * newScale));
}

extern "C" {
    CameraController* CameraController_create(int x, int y) {
        return new CameraController(x, y);
    }
    void CameraController_destroy(CameraController* instance) {
        delete instance;
    }
    void CameraController_StartLoop(CameraController* instance) {
        instance->startCaptureLoop();
    }
    Mat CameraController_getFrame(CameraController* instance) {
        return instance->getFrame();
    }
    void CameraController_StopLoop(CameraController* instance) {
        instance->stopCaptureLoop();
    }
}
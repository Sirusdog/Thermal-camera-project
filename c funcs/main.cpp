#include <iostream>
#include <stdio.h>
#include <opencv2/opencv.hpp>
#include "CameraController.hpp"

using namespace std;
using namespace cv;


int main() {
    CameraController camController(400, 400);
    while (true) {
        imshow("Test", camController.getFrame());
    };
    waitKey(0);
    return 0;
}
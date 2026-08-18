#include <iostream>
#include <stdio.h>
#include <opencv2/opencv.hpp>
#include "CameraController.hpp"
#include <raylib-cpp.hpp>

using namespace std;
using namespace cv;
using namespace raylib;

int main() {
    cout << "Running!" << endl;
    int screenX = GetScreenWidth();
    int screenY = GetScreenHeight();

    InitWindow(screenX, screenY, "Thermal Cam Render");

    CameraController cam = CameraController(400, 400);
    while (!WindowShouldClose()) {
        BeginDrawing();
        ClearBackground(RAYWHITE);
        Texture2D imgTex = LoadTextureFromImage(cam.getFrame());
        DrawTexture(imgTex, 0, 0, WHITE);
    };
    return 0;
}
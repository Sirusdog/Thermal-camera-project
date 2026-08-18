#include <iostream>
#include <stdio.h>
#include <opencv2/opencv.hpp>
#include "CameraController.hpp"
#include <raylib.h>

using namespace std;
using namespace cv;


int main() {
    cout << "Running!" << endl;
    int screenX = GetScreenWidth();
    int screenY = GetScreenHeight();

    InitWindow(screenX, screenY, "Thermal Cam Render");

    CameraController cam = camController(400, 400);
    while (!WindowShouldClose()) {
        BeginDrawing();
        ClearBackground(RAYWHITE);
        Texture2D imgTex = LoadTextureFromImage(cam.getFrame())
        DrawTexture(imgTex, 0, 0, WHITE)
    };
    return 0;
}
#include <iostream>
#include <stdio.h>
#include <opencv2/opencv.hpp>
#include "CameraController.hpp"
#include <raylib-cpp.hpp>

using namespace std;
using namespace cv;


int main() {
    cout << "Running!" << endl;
    int screenX = GetScreenWidth();
    int screenY = GetScreenHeight();

    raylib::InitWindow(screenX, screenY, "Thermal Cam Render");

    CameraController cam = CameraController(400, 400);
    while (!raylib::WindowShouldClose()) {
        raylib::BeginDrawing();
        raylib::ClearBackground(raylib::RAYWHITE);
        raylib::Texture2D imgTex = raylib::LoadTextureFromImage(cam.getFrame());
        raylib::DrawTexture(imgTex, 0, 0, raylib::WHITE);
    };
    return 0;
}
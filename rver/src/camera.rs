use opencv::prelude::*;
use opencv::{imgproc, core};
use std::time::SystemTime;

#[derive(PartialEq, Eq)]
pub enum VisMode{
    VIS_RAW = 0,
    VIS_OUTLINE = 1,
    VIS_THRESHOLD = 2,
    VIS_THRESHOLD_ADAPTIVE = 3
}

pub fn pp_frame(frame_in: &Mat, pallet: u32, visual_mode: VisMode) -> &Mat {
    let mut frame_i: Mat = Mat::default();
    let mut frame: Mat = Mat::default();
    let now = SystemTime::now();

    if (visual_mode == VisMode::VIS_OUTLINE) {
        imgproc::gaussian_blur(&frame_in, &mut frame_i, core::Size{width: 5, height: 5}, 1.0, 1.0, 4);
        imgproc::canny(&frame_i, &mut frame, 100.0, 200.0, 3, false);
    
    }
    else if (visual_mode == VisMode::VIS_THRESHOLD) {
        imgproc::threshold(&frame_in, &mut frame, 127.0, 255.0, imgproc::ThresholdTypes::THRESH_TOZERO.into());
    }
    else if (visual_mode == VisMode::VIS_THRESHOLD_ADAPTIVE) {
        imgproc::adaptive_threshold(&frame_in, &mut frame, 255.0, imgproc::AdaptiveThresholdTypes::ADAPTIVE_THRESH_GAUSSIAN_C.into(), imgproc::ThresholdTypes::THRESH_BINARY.into(), 11, 2.0);
    }
    else {
        frame = *frame_in;
    }
    let fps: String = (1.0 / now.elapsed()).to_string();
    println!(fps);
    imgproc::put_text(&mut frame, &fps, core::Point{x: 10, y: 10}, 0, 5.0, VecN<f64, 4>([256.0; 4]) , 5, -1, false);
    return &frame;

}
// Base code taken from https://github.com/twistedfall/opencv-rust/blob/master/examples/video_capture.rs
// By twistedfall
use opencv::prelude::*;
use opencv::{Result, highgui, videoio, imgproc, core};
use std::time::SystemTime;

mod menu;
mod camera;

fn main() -> Result<()> {
	let window = "video capture";
	highgui::named_window(window, highgui::WINDOW_GUI_NORMAL)?;
    highgui::set_window_property(window, highgui::WND_PROP_FULLSCREEN, 1.0);
	let mut cam = videoio::VideoCapture::new(0, videoio::CAP_ANY)?; // 0 is the default camera
	let opened = videoio::VideoCapture::is_opened(&cam)?;
	if !opened {
		panic!("Unable to open default camera!");
	}


	current_menu_index = 0;

	loop {
		let mut frame: Mat = Mat::default();
		cam.read(&mut frame);
		let frame_final: &Mat = pp_frame(&frame, imgproc::ColorMapTypes::COLORMAP_JET, VisMode::VIS_RAW);
        highgui::imshow(window, &frame);
		let key = highgui::wait_key(10)?;
		if key > 0 && key != 255 {
			break;
		}
	}
	Ok(())
}
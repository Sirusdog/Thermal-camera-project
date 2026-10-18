// Base code taken from https://github.com/twistedfall/opencv-rust/blob/master/examples/video_capture.rs
// By twistedfall
use opencv::prelude::*;
use opencv::{Result, highgui, videoio, imgproc};

fn main() -> Result<()> {
	let window = "video capture";
	highgui::named_window(window, highgui::WINDOW_GUI_NORMAL)?;
	let mut cam = videoio::VideoCapture::new(0, videoio::CAP_ANY)?; // 0 is the default camera
	let opened = videoio::VideoCapture::is_opened(&cam)?;
	if !opened {
		panic!("Unable to open default camera!");
	}
	loop {
		let mut frame = Mat::default();
		cam.read(&mut frame)?;
		if frame.size()?.width > 0 {
            resize(frame, frame, core::Size(600, 450), 2, 2, imgproc::INTER_LINEAR);
			highgui::imshow(window, &frame)?;
		}
		let key = highgui::wait_key(10)?;
		if key > 0 && key != 255 {
			break;
		}
	}
	Ok(())
}
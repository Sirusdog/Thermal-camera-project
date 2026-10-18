// Base code taken from https://github.com/twistedfall/opencv-rust/blob/master/examples/video_capture.rs
// By twistedfall
use opencv::prelude::*;
use opencv::{Result, highgui, videoio, imgproc, core};



fn main() -> Result<()> {
	let window = "video capture";
	highgui::named_window(window, highgui::WINDOW_GUI_NORMAL)?;
    highgui::set_window_property(window, highgui::WND_PROP_FULLSCREEN, 1.0);
	let mut cam = videoio::VideoCapture::new(0, videoio::CAP_ANY)?; // 0 is the default camera
	let opened = videoio::VideoCapture::is_opened(&cam)?;
	if !opened {
		panic!("Unable to open default camera!");
	}

	loop {
		let mut frame_pp = Mat::default();
        let mut frame_i = Mat::default()
        let mut frame = Mat::default();

		cam.read(&mut frame_pp)?;
		if frame_pp.size()?.width > 0 {
            imgproc::gaussian_blur(&frame_pp, frame_i, core::Size{width: 5, height: 5}, 1.0, 1.0, 4);
            imgproc::canny(&frame_i, &mut frame, 100.0, 200.0, 3, false);
			highgui::imshow(window, &frame);
		}
		let key = highgui::wait_key(10)?;
		if key > 0 && key != 255 {
			break;
		}
	}
	Ok(())
}
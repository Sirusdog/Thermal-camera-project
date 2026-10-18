// Base code taken from https://github.com/twistedfall/opencv-rust/blob/master/examples/video_capture.rs
// By twistedfall
use opencv::prelude::*;
use opencv::{Result, highgui, videoio, imgproc};

fn main() -> Result<()> {
	let window = "video capture";
	highgui::named_window(window, highgui::WINDOW_GUI_NORMAL)?;
    highgui::set_window_property(window, highgui::WND_PROP_FULLSCREEN, highgui::WND_FULLSCREEN);
	let mut cam = videoio::VideoCapture::new(0, videoio::CAP_ANY)?; // 0 is the default camera
	let opened = videoio::VideoCapture::is_opened(&cam)?;
	if !opened {
		panic!("Unable to open default camera!");
	}
	loop {
		let mut frame_pp = Mat::default();
        //let mut frame = Mat::default();

		cam.read(&mut frame_pp)?;
		if frame_pp.size()?.width > 0 {
            frame_pp.resize(1800);
			highgui::imshow(window, &frame_pp)?;
		}
		let key = highgui::wait_key(10)?;
		if key > 0 && key != 255 {
			break;
		}
	}
	Ok(())
}
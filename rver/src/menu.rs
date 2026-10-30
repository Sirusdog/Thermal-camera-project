//#![feature(default_field_values)]
use std::Vector;

pub enum MenuTypes {
    MENU_INT = 0,
    MENU_ARR = 1,
    MENU_BOOL = 2,
    MENU_FLOAT = 3,
    MENU_EXIT = 4,

}

pub enum ArbitTypes {
    AT_INT = 0,
    AT_BOOL = 1,
    AT_FLOAT = 2,
    AT_STRING = 3,
    AT_SPECIAL_STRING = 4,
}

struct ArbitraryType {
    
    // get pythoned idiot
    val: String,
    held_type: ArbitTypes,
    data_for: String,
}


trait GSI {
    fn increment(self);

    fn decrement(self);

    fn get(self) -> ArbitraryType;

    fn set(self, val: Option<T>);

    fn get_type(self) -> MenuTypes;
}

pub struct MenuInt {
    // Default variables shared will all menu types
    name: String,
    display_text: String,
    #[default]
    item_type: MenuTypes = MenuTypes::MENU_INT,
    current: u32,
    maximum: u32,
    minimum: u32
}

impl GSI for MenuInt {
    fn get(mut self) -> ArbitraryType {
        ArbitraryType{
            val: self.current.to_string(),
            held_type: ArbitTypes::AT_INT,
            data_for: self.name
        }
    }

    fn set(mut self, val: u32) {
        self.current = val;
    }

    fn increment(mut self) {
        self.current = self.current + 1;

        if (self.current >= self.maximum) {
            self.current = self.minimum;
        }
    }

    fn decrement(mut self) {
        self.current = self.current - 1;

        if (self.current <= self.minimum) {
            self.current = self.maximum;
        }
    }

    fn get_type(self) -> MenuTypes{
        return self.item_type;
    }
}

pub struct MenuFloat {
    // Default variables shared will all menu types
    name: String,
    display_text: String,
    #[default]
    item_type: MenuTypes = MenuTypes::MENU_FLOAT,


    current: f32,
    maximum: f32,
    minimum: f32,
    step_size: f32
}

impl GSI for MenuFloat {
    fn get(mut self) -> ArbitraryType {
        ArbitraryType{
            val: self.current.to_string(),
            held_type: ArbitTypes::AT_FLOAT,
            data_for: self.name
        }
    }

    fn set(mut self, val: f32) {
        self.current = val;
    }

    fn increment(mut self) {
        self.current = self.current + self.step_size;

        if (self.current >= self.maximum) {
            self.current = self.minimum;
        }
    }

    fn decrement(mut self) {
        self.current = self.current - self.step_size;

        if (self.current <= self.minimum) {
            self.current = self.maximum;
        }
    }

    fn get_type(self) -> MenuTypes{
        return self.item_type;
    }
}

pub struct MenuArr {
    // Default variables shared will all menu types
    name: String,
    display_text: String,
    #[default]
    item_type: MenuTypes = MenuTypes::MENU_ARR,


    current: u32,
    vals: Vec<String> = vec![]
}

impl GSI for MenuArr {
    fn get(mut self) -> ArbitraryType {
        ArbitraryType{
            val: self.vals[self.current as usize],
            held_type: ArbitTypes::AT_STRING,
            data_for: self.name
        }
    }

    fn set(mut self, val:u32) {
        self.current = val;
    }

    fn increment(mut self) {
        self.current = self.current + 1;

        if (self.current >= self.vals.len() as u32) {
            self.current = 0;
        }
    }

    fn decrement(mut self) {
        self.current = self.current - 1;

        if (self.current <= 0) {
            self.current = self.vals.len() as u32;
        }
    }
    
    fn get_type(self) -> MenuTypes{
        return self.item_type;
    }
}

pub struct MenuBool {
    // Default variables shared will all menu types
    name: String,
    display_text: String,
    #[default]
    item_type: MenuTypes = MenuTypes::MENU_BOOL,

    current: bool

}

impl GSI for MenuBool {
    fn get(mut self) -> ArbitraryType {
        ArbitraryType{
            val: self.current.to_string(),
            held_type: ArbitTypes::AT_BOOL,
            data_for: self.name
        }
    }

    fn set(mut self, val: bool) {
        self.current = val;
    }

    fn increment(mut self) {
        !self.current;
    }

    fn decrement(mut self) {
        !self.current;
    }
    
    fn get_type(self) -> MenuTypes{
        return self.item_type;
    }
}

pub struct MenuExit {
    // Default variables shared will all menu types
    name: String,
    display_text: String,
    #[default]
    item_type: MenuTypes = MenuTypes::MENU_EXIT
}

impl GSI for MenuExit {
    fn get(mut self) -> ArbitraryType {
        ArbitraryType{
            val: 1.to_string(),
            held_type: ArbitTypes::AT_SPECIAL_STRING,
            data_for: self.name
        }
    }

    fn set(mut self, val: bool) {

    }

    fn increment(mut self) {

    }

    fn decrement(mut self) {

    }
    
    fn get_type(self) -> MenuTypes{
        return self.item_type;
    }
}
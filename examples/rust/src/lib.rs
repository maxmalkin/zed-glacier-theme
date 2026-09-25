//! A small cache with traits, lifetimes, generics, and pattern matching.
use std::fmt::Display;

pub const MAX_ENTRIES: usize = 128;

#[derive(Debug, Clone, PartialEq)]
pub enum CacheResult<T> {
    Hit(T),
    Miss,
}

pub trait Render {
    fn render(&self) -> String;
}

#[derive(Debug)]
pub struct Cache<'a, T> {
    pub label: &'a str,
    entries: Vec<T>,
}

impl<'a, T: Display + Clone> Cache<'a, T> {
    pub fn new(label: &'a str) -> Self {
        Self { label, entries: Vec::new() }
    }

    pub fn insert(&mut self, value: T) -> Result<usize, &'static str> {
        let mut count = self.entries.len();
        if count >= MAX_ENTRIES {
            return Err("cache is full\n");
        }
        self.entries.push(value);
        count += 1;
        Ok(count)
    }

    pub fn get(&self, index: usize) -> CacheResult<T> {
        match self.entries.get(index) {
            Some(value) => CacheResult::Hit(value.clone()),
            None => CacheResult::Miss,
        }
    }
}

impl<T: Display + Clone> Render for Cache<'_, T> {
    fn render(&self) -> String {
        let enabled = true;
        format!("{}: {} entries (enabled={enabled})", self.label, self.entries.len())
    }
}

/// The pointer must be valid and aligned for reads of one `u8`.
pub unsafe fn read_byte(pointer: *const u8) -> u8 {
    unsafe { *pointer }
}

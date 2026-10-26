//! The task store: a list of tasks saved as JSON. No command-line code here,
//! so the logic is easy to test (see tests/store.rs).

use serde::{Deserialize, Serialize};
use std::path::Path;
use std::{fs, io};
use thiserror::Error;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Task {
    pub id: u32,
    pub title: String,
    pub done: bool,
}

/// Everything that can go wrong in the library, as one enum.
#[derive(Debug, Error)]
pub enum StoreError {
    #[error("could not read or write the task file")]
    Io(#[from] io::Error),
    #[error("the task file is not valid JSON")]
    Json(#[from] serde_json::Error),
    #[error("no task with id {0}")]
    NotFound(u32),
    #[error("a task title cannot be empty")]
    EmptyTitle,
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct Store {
    next_id: u32,
    tasks: Vec<Task>,
}

impl Store {
    /// Loads the store, or returns an empty one if the file does not exist yet.
    pub fn load(path: &Path) -> Result<Store, StoreError> {
        match fs::read_to_string(path) {
            Ok(text) => Ok(serde_json::from_str(&text)?),
            Err(e) if e.kind() == io::ErrorKind::NotFound => Ok(Store::default()),
            Err(e) => Err(e.into()),
        }
    }

    pub fn save(&self, path: &Path) -> Result<(), StoreError> {
        let text = serde_json::to_string_pretty(self)?;
        fs::write(path, text)?;
        Ok(())
    }

    pub fn add(&mut self, title: &str) -> Result<&Task, StoreError> {
        let title = title.trim();
        if title.is_empty() {
            return Err(StoreError::EmptyTitle);
        }
        self.next_id += 1;
        self.tasks.push(Task { id: self.next_id, title: title.to_string(), done: false });
        Ok(self.tasks.last().expect("just pushed"))
    }

    pub fn complete(&mut self, id: u32) -> Result<&Task, StoreError> {
        let task = self.tasks.iter_mut().find(|t| t.id == id).ok_or(StoreError::NotFound(id))?;
        task.done = true;
        Ok(task)
    }

    pub fn remove(&mut self, id: u32) -> Result<Task, StoreError> {
        let index = self.tasks.iter().position(|t| t.id == id).ok_or(StoreError::NotFound(id))?;
        Ok(self.tasks.remove(index))
    }

    /// Tasks to show: all of them, or only the open ones.
    pub fn list(&self, include_done: bool) -> impl Iterator<Item = &Task> {
        self.tasks.iter().filter(move |t| include_done || !t.done)
    }
}

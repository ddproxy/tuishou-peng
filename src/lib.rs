#![forbid(unsafe_code)]

//! Shared capacity and limits code for [Tuishou](https://github.com/ddproxy/tuishou).

/// The crate version, taken from `CARGO_PKG_VERSION` at compile time.
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

#[cfg(test)]
mod tests {
    use super::VERSION;

    #[test]
    fn version_matches_package_version() {
        assert_eq!(VERSION, env!("CARGO_PKG_VERSION"));
    }
}

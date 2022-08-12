## [0.1.2] - 2022-08-12

### Added
- The `row` strategy can be used instead of `product` (`product` remains the default).  This uses the `zip` function internally to create the dictionary used in string formatting.  So, the following parameters: `[1, 2]` and `[3, 4]` would result in `[(1, 3), (2, 4)]`.
- Test case for the row strategy using a SQL query containing multiple columns

## [0.1.1] - 2022-08-10

### Fixed
- Fixed the reference for the CLI script within `pyproject.toml`

## [0.1.0] - 2022-08-10

### Added
- Initial functionality to create dynamic models
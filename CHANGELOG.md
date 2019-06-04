### [0.2.0] - 04-06-2019 

**Compatibility breaking changes**

#### Added
- All website are reported as down
- Form register and refactor default forms to use this
- Add custom form urls + shortcut model_url function
- Add layout register + layout views
- Add model verbose_name field + change choices to use verbose_name query
- Add permission checks and hide menu/buttons with no permission

#### Changed
- Render fields for verbose_name and search title/description
- Move all dependencies handling to setup.py
- Upgrade to Django 2.2 and update other dependencies
- refactor views/core from Django app to Trionyx package
- Rename navigation to menu
- Move navigtaion.tabs to views.tabs
- Quickstart project settings layout + add environment.json

#### Fixed
- Cant search in fitler select field
- Datetimepicker not working for time
- Travis build error
- Button component


### [0.1.1] - 30-05-2019
#### Fixed
- Search for not indexed models
- Lint errors


### [0.1.0] - 30-05-2019
#### Added
- Global search
- Add filters to model list page
- Set default form layouts for fields

#### Changed
- Search for not indexed models

#### Fixed
- Make datepicker work with locale input format
- On menu hover resize header 
- Keep menu state after page refresh
- Search for not indexed models
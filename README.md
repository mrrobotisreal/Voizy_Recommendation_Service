# Voizy Recommendation Service

![Cover Image](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/VoizyDocumentationCoverImage.png)

### What is "Voizy"?

> _"Voizy is your new social playground—share, connect, and vibe without ads or creepy tracking. Social media the way it was meant to be!"_
>
> _**Your voice. Your vibe. Voizy.**_

**Voizy** is a _social media app_ written entirely in **Kotlin** and **Jetpack Compose** for the _Android UI_, **Java** for the backend server, and **MySQL** for the database. Create your account, update your profile info, add images, pick a profile pic and a cover pic, upload a song to be played when people visit your profile (courtesy of _Epidemic Sound_), search for people and send friend requests, publish posts to the main feed or on a friend's page, react to posts, leave comments on posts and react to comments, re-post someone else's post with your own thoughts, create posts with images, location, hashtags, groups, and tags added, create a poll on your post to see everyone's answers and generate interactions, view recommended posts in different feeds, join and create groups that others can join where you can discuss certain topics, get notifications of new posts and customize which notifications you'd like to receive, and so much more!

## Table of Contents

- [Contact info](#contact-info)
- [Features](#features)
- [Demo](#demo)
- [Getting started](#getting-started)
- [Usage](#usage)
- [Testing](#testing)
- [Documentation](#documentation)
- [Technologies](#technologies)
- [License](#license)

## Contact info

**Developed by:** <span style="color: yellow;">Mitchell Wintrow</span>

**Email**: owner@winapps.io, mitchellwintrow@gmail.com

## Features

- 🔒 Secure user authentication
- 🖊️ Update your profile information so people know who you and what you like
- 🎵 Customize your profile to play a theme that matches your vibe when people view it (🚧 _in development..._ 🛠️)
- 📸 Add photos or take new photos and add them to your profile and posts
- 📍 Add locations to your posts
- 🏷️ Add custom hashtags for optimized search results and trends (🚧 _in development..._ 🛠️)
- 🔎 Filter posts to make finding older posts or posts with specific content easier (🚧 _in development..._ 🛠️)
- 🕸️ Search for people and send friend requests to grow your network
- 🤝 Create and join groups where people can discuss certain topics (🚧 _in development..._ 🛠️)
- 🔔 Customize notifications and follow accounts and groups for updates (🚧 _in development..._ 🛠️)

## Demo

**Quick Walkthrough Demo**

_1. Home Screen (Recommended Posts) & Feeds Screen_, _2. Groups Screen & People Screen_

![fastXS_Demo1_HomeAndFeeds](https://github.com/user-attachments/assets/e7a6065e-8382-4dfa-bf99-ec2fea9cb593)
![fastXS_Demo2_GroupsAndPeople](https://github.com/user-attachments/assets/c1d81bfb-f6a4-4504-9b27-b7ef226ef56a)

_1. Profile Screen_, _2. App & Profile Preferences_, _3. Create a Post_

![fastXS_Demo3_Profile](https://github.com/user-attachments/assets/9f38eea7-d859-4e65-9398-34f697159a35)
![fastXS_Demo4_Preferences](https://github.com/user-attachments/assets/36d31f80-2a43-4c1a-93a8-2a94d300f342)
![fastXS_Demo5_CreatePost](https://github.com/user-attachments/assets/db02f457-c36a-47e8-9854-973402aed81e)

![Login Screen](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy33.jpg)
![Create Account Screen](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy34.jpg)
![Home Screen](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy1.jpg)
![React to Post](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy5.jpg)
![Comment on Post](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy4.jpg)
![Create Post Dialog](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy27.jpg)
![Create Post Dialog](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy31.jpg)
![Photos](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy11.jpg)
![Add Images](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy9.jpg)
![About - Profile Info](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy22.jpg)
![Friends](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy23.jpg)
![Search Friends](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/main_profile/readme/voizy24.jpg)

🚧 More coming soon... 🛠️

_Thanks for your patience!_

## Getting Started

Instructions for getting started will be added soon... Thanks for your patience!

## Usage

Instructions for the usage of this app will be added soon... Thanks for your patience!

## Testing

There are currently `45` tests implemented as seen in the screenshot below. Follow the instructions underneath to run all tests.

![TestRun](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/portfolio/voizy/demos/java_server_test_runs/2025_03_22/java_test_2025_03_22_run2_scaleddown.jpg)

To run the entire suite of tests for the Voizy server you simply need to set a few environment variables and then run it as you normally would via `./gradlew test`. Below are the environment variables that need to be set in order to run all the tests for the entire package (_NOTE: You'll need to make sure that you have a test database already created that is named "voizy_test"_):

```bash
export DBU='root'
export DBP='<your-password>'
export TEST_MODE='true'

./gradlew test
```

## Documentation

You can find the official **Voizy** <em style="color: yellow;">Documentation</em> here:

- [Official **Documentation**](https://winapps.io/projects/voizy/documentation)

You can find the official **Voizy** <em style="color: yellow;">Privacy Policy</em> here:

- [Official **Privacy Policy**](https://winapps.io/projects/voizy/privacy-policy)

## Technologies

**Languages**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff) ![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white) ![NumPy](https://img.shields.io/badge/NumPy-4DABCF?logo=numpy&logoColor=fff) ![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=fff) ![LightFM](https://img.shields.io/badge/LightFM-%23ffffff.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC0AAAAtCAYAAAA6GuKaAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAFoWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSfvu78nIGlkPSdXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQnPz4KPHg6eG1wbWV0YSB4bWxuczp4PSdhZG9iZTpuczptZXRhLyc+CjxyZGY6UkRGIHhtbG5zOnJkZj0naHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyc+CgogPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9JycKICB4bWxuczpBdHRyaWI9J2h0dHA6Ly9ucy5hdHRyaWJ1dGlvbi5jb20vYWRzLzEuMC8nPgogIDxBdHRyaWI6QWRzPgogICA8cmRmOlNlcT4KICAgIDxyZGY6bGkgcmRmOnBhcnNlVHlwZT0nUmVzb3VyY2UnPgogICAgIDxBdHRyaWI6Q3JlYXRlZD4yMDI1LTA0LTA1PC9BdHRyaWI6Q3JlYXRlZD4KICAgICA8QXR0cmliOkV4dElkPjgyNWY2YTgyLWMwYjktNGNhZi1hZjllLTFmZTU4ZWY5NmE3NjwvQXR0cmliOkV4dElkPgogICAgIDxBdHRyaWI6RmJJZD41MjUyNjU5MTQxNzk1ODA8L0F0dHJpYjpGYklkPgogICAgIDxBdHRyaWI6VG91Y2hUeXBlPjI8L0F0dHJpYjpUb3VjaFR5cGU+CiAgICA8L3JkZjpsaT4KICAgPC9yZGY6U2VxPgogIDwvQXR0cmliOkFkcz4KIDwvcmRmOkRlc2NyaXB0aW9uPgoKIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PScnCiAgeG1sbnM6Q29udGFpbnNBaUdlbmVyYXRlZENvbnRlbnQ9J2h0dHBzOi8vY2FudmEuY29tL2V4cG9ydCc+CiAgPENvbnRhaW5zQWlHZW5lcmF0ZWRDb250ZW50OkNvbnRhaW5zQWlHZW5lcmF0ZWRDb250ZW50PlllczwvQ29udGFpbnNBaUdlbmVyYXRlZENvbnRlbnQ6Q29udGFpbnNBaUdlbmVyYXRlZENvbnRlbnQ+CiA8L3JkZjpEZXNjcmlwdGlvbj4KCiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0nJwogIHhtbG5zOmRjPSdodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyc+CiAgPGRjOnRpdGxlPgogICA8cmRmOkFsdD4KICAgIDxyZGY6bGkgeG1sOmxhbmc9J3gtZGVmYXVsdCc+bGlnaHRGTUJhZGdlIC0gMTwvcmRmOmxpPgogICA8L3JkZjpBbHQ+CiAgPC9kYzp0aXRsZT4KIDwvcmRmOkRlc2NyaXB0aW9uPgoKIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PScnCiAgeG1sbnM6cGRmPSdodHRwOi8vbnMuYWRvYmUuY29tL3BkZi8xLjMvJz4KICA8cGRmOkF1dGhvcj5NaXRjaCBXaW50cm93PC9wZGY6QXV0aG9yPgogPC9yZGY6RGVzY3JpcHRpb24+CgogPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9JycKICB4bWxuczp4bXA9J2h0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8nPgogIDx4bXA6Q3JlYXRvclRvb2w+Q2FudmEgKFJlbmRlcmVyKSBkb2M9REFHanZhTERHUXcgdXNlcj1VQUZBdXI5d1hoMCBicmFuZD1CQUZBdXBOeGJKbyB0ZW1wbGF0ZT08L3htcDpDcmVhdG9yVG9vbD4KIDwvcmRmOkRlc2NyaXB0aW9uPgo8L3JkZjpSREY+CjwveDp4bXBtZXRhPgo8P3hwYWNrZXQgZW5kPSdyJz8+wpznzAAAAnVJREFUeJzt2EuoTVEcx/HPPvd6v98jKQlJEkoYMiEpJTOUx0REKSNDlBJRyqsMhFCSESUzr0gxUKKYiCKUvLnHYK2T0+ls9t7cfd3a39qt/V9rr///d9Ze67/W2YleSNLTAopQiS6LSnRZVKLLohJdFr1SdK3pvh/65+jbiQF/8D2oTX2CwTnitHUMw3ARVzA2Y99DuI1pKe07cQfzWuq34R6W5VLaREP0eCzCAkzJ2G8NpmNxm/YEqzA1+m2uX4FJWFJM8i/RSbxP0BHrOtAnpV/zc50p7Y36jpa2zpb+uaml1PfFHpzAmKLOu4s00cOxHisxUxiZtdgtzP92LMdejMupYa6wPmZFe0a050d7Mg5iYaNDu1cLb7BDWJS3hJHfhyF4gPMtzyc4glF4jgM5RG8XfvAQrMZmrMMELI33mzAH11BPE92FF/gWr5qQptLSVSK8gQRDcwhu+MtaIn2kR+MYBuIJbuQQ0u2kie4jjFhN+hzuMdIW4n9NJbosKtFl0RD9BR/wGR+F3Py+qWylS9iAfsSyjtdN9fVYduHdb+LXY3vjuTT7R7OfRsp7ii3Cmfo+vmOjcO64nhJsrXAsPRvt1cKudSraG4Wt+MxvRMMuPMS5aO/HS1yK9lF8wtXoN/M/l354JRzqV+F0xn6tJMIZezaOY0MRJ2mbSytfhTPCJFwuEuhfklV0Hc9i+anb1GQkq+i+OIkRwjS58Bcx6/EqTNaU1yEIrmHkX8SrC4vuAx4VdZJ1pBsB/wVbcVjIUoXIOtLf8VjI2U+LBou8xU1hPyhEno81E4Vz9l0h+fcYvfILUyW6LCrRZVGJLotKdFn8BKemcpNjsripAAAAAElFTkSuQmCC) ![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?logo=scikit-learn&logoColor=white) ![SciPy](https://img.shields.io/badge/SciPy-%230C55A5.svg?logo=scipy&logoColor=%white) (Backend ML Service)

![Java](https://img.shields.io/badge/Java-%23ED8B00.svg?logo=openjdk&logoColor=white) (Backend)

![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=fff) (Database)

![Kotlin](https://img.shields.io/badge/Kotlin-%237F52FF.svg?logo=kotlin&logoColor=white) (Android UI)

**OS Platforms**

![Android](https://img.shields.io/badge/Android-3DDC84?logo=android&logoColor=white)

**IDEs & Text Editors**

![PyCharm](https://img.shields.io/badge/PyCharm-000?logo=pycharm&logoColor=fff)
![Android Studio](https://img.shields.io/badge/Android%20Studio-346ac1?&logo=android%20studio&logoColor=white)
![Neovim](https://img.shields.io/badge/Neovim-57A143?logo=neovim&logoColor=fff)

**Design**

![Canva](https://img.shields.io/badge/Canva-%2300C4CC.svg?&logo=Canva&logoColor=white)

**Documentation**

![Notion](https://img.shields.io/badge/Notion-000?logo=notion&logoColor=fff)

**Version Control**

![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=fff)

**Producer & Developer**

[![WinApps.io](https://img.shields.io/badge/WinApps-%232f56a0.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAACXBIWXMAAAk6AAAJOgHwZJJKAAACB1BMVEVHcEz////+/v79/f3+/v7+/v7////////////7+/v+/v78/Pz+/v79/f39/f39/f37+/v8/Pz9/f3+/v7+/v7+/v7+/v79/f38/Pz+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v739/f9/f34+Pj5+fn5+fn5+fn7+/v7+/v7+/v7+/v7+/v8/Pz8/Pzl5eX8/Pz9/f39/f3x8fH8/Pz+/v7+/v7+/v79/f39/f3+/v7+/v79/f39/f39/f39/f39/f39/f38/Pz+/v7+/v719fX19fX+/v7+/v78/Pz9/f39/f38/Pz9/f3p6en39/f29vb39/f39/f39/f39/f39/f+/v66urr+/v79/f38/Pz9/f39/f38/Pz9/f35+fn5+fn5+fn4+Pj4+Pj+/v77+/v7+/vu7u77+/v6+vr7+/v7+/v7+/v6+vrLy8v6+vr6+vru7u7j4+P7+/v8/Pz8/Pz9/f39/f39/f38/Pz8/Pzx8fH+/v7+/v7a2trz8/Pb29v+/v7+/v7+/v7n5+fz8/P+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v79/f39/f39/f3+/v7+/v7+/v7+/v7+/v79/f39/f39/f39/f39/f38/Pz9/f39/f39/f39/f39/f39/f39/f3+/v7+/v7+/v7+/v7+/v48I/X5AAAArHRSTlMAA/oDBfn99wEBvZfRSHtYAnBqbuvI48KJ2ebsxfLdvqJ/E2kBHSAPPTE7DxNeNwVsT1sGJkD06byZwc6ioce5kIyBurAMC0ddE39lZ0QDGx0XGBURBiMBBiNGUgYZBCQJGRIXdnAKATcpRGIeFgEyLwQDODUsd3gvMCAIUzEDDAF6fV8BCoqc5a+rzJCPtpue1vGGnbLV27WJ4J+3z8zSiu2wpbq0q6mh0t64yjchRwAABL1pVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0n77u/JyBpZD0nVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkJz8+Cjx4OnhtcG1ldGEgeG1sbnM6eD0nYWRvYmU6bnM6bWV0YS8nPgo8cmRmOlJERiB4bWxuczpyZGY9J2h0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMnPgoKIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PScnCiAgeG1sbnM6QXR0cmliPSdodHRwOi8vbnMuYXR0cmlidXRpb24uY29tL2Fkcy8xLjAvJz4KICA8QXR0cmliOkFkcz4KICAgPHJkZjpTZXE+CiAgICA8cmRmOmxpIHJkZjpwYXJzZVR5cGU9J1Jlc291cmNlJz4KICAgICA8QXR0cmliOkNyZWF0ZWQ+MjAyNS0wMi0xMDwvQXR0cmliOkNyZWF0ZWQ+CiAgICAgPEF0dHJpYjpFeHRJZD5kY2RmNDhiOC03ODRiLTQ3OWEtYjA1ZS05MjNkM2I1MzM1ZmI8L0F0dHJpYjpFeHRJZD4KICAgICA8QXR0cmliOkZiSWQ+NTI1MjY1OTE0MTc5NTgwPC9BdHRyaWI6RmJJZD4KICAgICA8QXR0cmliOlRvdWNoVHlwZT4yPC9BdHRyaWI6VG91Y2hUeXBlPgogICAgPC9yZGY6bGk+CiAgIDwvcmRmOlNlcT4KICA8L0F0dHJpYjpBZHM+CiA8L3JkZjpEZXNjcmlwdGlvbj4KCiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0nJwogIHhtbG5zOmRjPSdodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyc+CiAgPGRjOnRpdGxlPgogICA8cmRmOkFsdD4KICAgIDxyZGY6bGkgeG1sOmxhbmc9J3gtZGVmYXVsdCc+Q29weSBvZiBXaW5BcHBzX0JhZGdlX1doaXRlIC0gMTwvcmRmOmxpPgogICA8L3JkZjpBbHQ+CiAgPC9kYzp0aXRsZT4KIDwvcmRmOkRlc2NyaXB0aW9uPgoKIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PScnCiAgeG1sbnM6cGRmPSdodHRwOi8vbnMuYWRvYmUuY29tL3BkZi8xLjMvJz4KICA8cGRmOkF1dGhvcj5NaXRjaCBXaW50cm93PC9wZGY6QXV0aG9yPgogPC9yZGY6RGVzY3JpcHRpb24+CgogPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9JycKICB4bWxuczp4bXA9J2h0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8nPgogIDx4bXA6Q3JlYXRvclRvb2w+Q2FudmEgZG9jPURBR2V2a2dwblBBIHVzZXI9VUFGQXVyOXdYaDAgYnJhbmQ9QkFGQXVwTnhiSm8gdGVtcGxhdGU9PC94bXA6Q3JlYXRvclRvb2w+CiA8L3JkZjpEZXNjcmlwdGlvbj4KPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KPD94cGFja2V0IGVuZD0ncic/PupbsSAAAAIcSURBVCgVVVIHWxNBEH13Ry7BJHIBkpACCSJKVUBIAlgAsfeO7eyKXexiwdh7V1TsXXk/0tk08d337c1OeVN2gDwsV07SpuZVhb8B1Lk9nnn7dgBWQZsVDKwK0hEKk46emRDPCTBQz8il/ThweT75fsp/sRZqmTqWdf5FfrgyIU7Ej1GgqNjQigAP+QlawWyjpXIn7BxZK03HNBQXrCOfOzJyw5do74KrVeTZQk0WBn0Hz32NRb/pJIOIk/15Xun50HfRKui6k3Vp8neBFBWiNZVNDp1tZeSf1VmrC25lcoxfu/5DIsldt8jxvlKV1cBhOsnq6eI6a5JE+yDn7fOJNarg3eXknfa1cX/8CG4sWnwBw06TLYj9VDWVksklR1WdocZMoqU0E7Xo4LDcUqQXnXRKncuApoquhMkemUf5ZGAgxLvAPalSZxqNHmFgYJ2Mq/++pAyzBFhOU9pYgRph0GW0toYHYeBmgJvhwmwJSK5Hb4ZhDjQDD5ObAD83qolvqTQZx1bpVKf0aONRlRSUFlpbvufSbh9eCMPLldiG7ewU4x52A7aFi6NC+XjodFmrKFUTxyGdNvOJXAYwgxIbqFGj2uD1062SWfDxqVc0OPFMDVJ/FesaJVNDmfd2oaGbkddvqsua50rGLNwnVaBAZli/dywYfdeGklRElvPt2Kl/y2vkl108m84Mti8UkzxJHpatWZZmIecmksJfW1eka4cCl0kAAAAASUVORK5CYII=&style=flat&labelColor=%232f56a0)](https://winapps.io/)
[![Mitchell Wintrow](https://img.shields.io/badge/Mitchell_Wintrow-%23ff6f00.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAACXBIWXMAAAk6AAAJOgHwZJJKAAACB1BMVEVHcEz////+/v79/f3+/v7+/v7////////////7+/v+/v78/Pz+/v79/f39/f39/f37+/v8/Pz9/f3+/v7+/v7+/v7+/v79/f38/Pz+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v739/f9/f34+Pj5+fn5+fn5+fn7+/v7+/v7+/v7+/v7+/v8/Pz8/Pzl5eX8/Pz9/f39/f3x8fH8/Pz+/v7+/v7+/v79/f39/f3+/v7+/v79/f39/f39/f39/f39/f39/f38/Pz+/v7+/v719fX19fX+/v7+/v78/Pz9/f39/f38/Pz9/f3p6en39/f29vb39/f39/f39/f39/f39/f+/v66urr+/v79/f38/Pz9/f39/f38/Pz9/f35+fn5+fn5+fn4+Pj4+Pj+/v77+/v7+/vu7u77+/v6+vr7+/v7+/v7+/v6+vrLy8v6+vr6+vru7u7j4+P7+/v8/Pz8/Pz9/f39/f39/f38/Pz8/Pzx8fH+/v7+/v7a2trz8/Pb29v+/v7+/v7+/v7n5+fz8/P+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v79/f39/f39/f3+/v7+/v7+/v7+/v7+/v79/f39/f39/f39/f39/f38/Pz9/f39/f39/f39/f39/f39/f39/f3+/v7+/v7+/v7+/v7+/v48I/X5AAAArHRSTlMAA/oDBfn99wEBvZfRSHtYAnBqbuvI48KJ2ebsxfLdvqJ/E2kBHSAPPTE7DxNeNwVsT1sGJkD06byZwc6ioce5kIyBurAMC0ddE39lZ0QDGx0XGBURBiMBBiNGUgYZBCQJGRIXdnAKATcpRGIeFgEyLwQDODUsd3gvMCAIUzEDDAF6fV8BCoqc5a+rzJCPtpue1vGGnbLV27WJ4J+3z8zSiu2wpbq0q6mh0t64yjchRwAABL1pVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0n77u/JyBpZD0nVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkJz8+Cjx4OnhtcG1ldGEgeG1sbnM6eD0nYWRvYmU6bnM6bWV0YS8nPgo8cmRmOlJERiB4bWxuczpyZGY9J2h0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMnPgoKIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PScnCiAgeG1sbnM6QXR0cmliPSdodHRwOi8vbnMuYXR0cmlidXRpb24uY29tL2Fkcy8xLjAvJz4KICA8QXR0cmliOkFkcz4KICAgPHJkZjpTZXE+CiAgICA8cmRmOmxpIHJkZjpwYXJzZVR5cGU9J1Jlc291cmNlJz4KICAgICA8QXR0cmliOkNyZWF0ZWQ+MjAyNS0wMi0xMDwvQXR0cmliOkNyZWF0ZWQ+CiAgICAgPEF0dHJpYjpFeHRJZD5kY2RmNDhiOC03ODRiLTQ3OWEtYjA1ZS05MjNkM2I1MzM1ZmI8L0F0dHJpYjpFeHRJZD4KICAgICA8QXR0cmliOkZiSWQ+NTI1MjY1OTE0MTc5NTgwPC9BdHRyaWI6RmJJZD4KICAgICA8QXR0cmliOlRvdWNoVHlwZT4yPC9BdHRyaWI6VG91Y2hUeXBlPgogICAgPC9yZGY6bGk+CiAgIDwvcmRmOlNlcT4KICA8L0F0dHJpYjpBZHM+CiA8L3JkZjpEZXNjcmlwdGlvbj4KCiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0nJwogIHhtbG5zOmRjPSdodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyc+CiAgPGRjOnRpdGxlPgogICA8cmRmOkFsdD4KICAgIDxyZGY6bGkgeG1sOmxhbmc9J3gtZGVmYXVsdCc+Q29weSBvZiBXaW5BcHBzX0JhZGdlX1doaXRlIC0gMTwvcmRmOmxpPgogICA8L3JkZjpBbHQ+CiAgPC9kYzp0aXRsZT4KIDwvcmRmOkRlc2NyaXB0aW9uPgoKIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PScnCiAgeG1sbnM6cGRmPSdodHRwOi8vbnMuYWRvYmUuY29tL3BkZi8xLjMvJz4KICA8cGRmOkF1dGhvcj5NaXRjaCBXaW50cm93PC9wZGY6QXV0aG9yPgogPC9yZGY6RGVzY3JpcHRpb24+CgogPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9JycKICB4bWxuczp4bXA9J2h0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8nPgogIDx4bXA6Q3JlYXRvclRvb2w+Q2FudmEgZG9jPURBR2V2a2dwblBBIHVzZXI9VUFGQXVyOXdYaDAgYnJhbmQ9QkFGQXVwTnhiSm8gdGVtcGxhdGU9PC94bXA6Q3JlYXRvclRvb2w+CiA8L3JkZjpEZXNjcmlwdGlvbj4KPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KPD94cGFja2V0IGVuZD0ncic/PupbsSAAAAIcSURBVCgVVVIHWxNBEH13Ry7BJHIBkpACCSJKVUBIAlgAsfeO7eyKXexiwdh7V1TsXXk/0tk08d337c1OeVN2gDwsV07SpuZVhb8B1Lk9nnn7dgBWQZsVDKwK0hEKk46emRDPCTBQz8il/ThweT75fsp/sRZqmTqWdf5FfrgyIU7Ej1GgqNjQigAP+QlawWyjpXIn7BxZK03HNBQXrCOfOzJyw5do74KrVeTZQk0WBn0Hz32NRb/pJIOIk/15Xun50HfRKui6k3Vp8neBFBWiNZVNDp1tZeSf1VmrC25lcoxfu/5DIsldt8jxvlKV1cBhOsnq6eI6a5JE+yDn7fOJNarg3eXknfa1cX/8CG4sWnwBw06TLYj9VDWVksklR1WdocZMoqU0E7Xo4LDcUqQXnXRKncuApoquhMkemUf5ZGAgxLvAPalSZxqNHmFgYJ2Mq/++pAyzBFhOU9pYgRph0GW0toYHYeBmgJvhwmwJSK5Hb4ZhDjQDD5ObAD83qolvqTQZx1bpVKf0aONRlRSUFlpbvufSbh9eCMPLldiG7ewU4x52A7aFi6NC+XjodFmrKFUTxyGdNvOJXAYwgxIbqFGj2uD1062SWfDxqVc0OPFMDVJ/FesaJVNDmfd2oaGbkddvqsua50rGLNwnVaBAZli/dywYfdeGklRElvPt2Kl/y2vkl108m84Mti8UkzxJHpatWZZmIecmksJfW1eka4cCl0kAAAAASUVORK5CYII=&style=flat)](https://winapps.io/about/mitchell-wintrow)

![Mitchell Wintrow Profile Pic](https://winapps-solutions-llc.s3.us-west-2.amazonaws.com/mitchProfilePic.png)

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License**.

- You can view and share this code for **non-commercial purposes** as long as proper credit is given.
- **Forking, modifications, or derivative works are not allowed.**

For the full license text, visit [Creative Commons License](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode).

---

This product is developed and owned by [WinApps (Mitchell Wintrow) ©2024](https://winapps.io)

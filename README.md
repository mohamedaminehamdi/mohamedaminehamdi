<a href="https://github.com/mohamedaminehamdi">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mohamedaminehamdi/mohamedaminehamdi/main/dark_mode.svg">
    <img alt="Mohamed Amine Hamdi, DevSecOps Engineer. Linux, Kubernetes, AWS." src="https://raw.githubusercontent.com/mohamedaminehamdi/mohamedaminehamdi/main/light_mode.svg">
  </picture>
</a>

<p align="center">
  <a href="https://www.linkedin.com/in/mohamed-amine-hamdi/"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/buttons/linkedin-dark.svg"><img src="assets/buttons/linkedin-light.svg" width="23.5%" alt="LinkedIn mohamed-amine-hamdi"></picture></a>
  <a href="https://medium.com/@mohamedaminehamdi"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/buttons/medium-dark.svg"><img src="assets/buttons/medium-light.svg" width="23.5%" alt="Medium @mohamedaminehamdi"></picture></a>
  <a href="https://dev.to/mohamedaminehamdi"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/buttons/dev-dark.svg"><img src="assets/buttons/dev-light.svg" width="23.5%" alt="DEV @mohamedaminehamdi"></picture></a>
  <a href="https://x.com/aminehamdibarca"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/buttons/x-dark.svg"><img src="assets/buttons/x-light.svg" width="23.5%" alt="X @aminehamdibarca"></picture></a>
</p>

<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://streak-stats.demolab.com/?user=mohamedaminehamdi&background=161b22&border=30363d&stroke=30363d&ring=ffa657&fire=ffa657&currStreakNum=c9d1d9&sideNums=c9d1d9&currStreakLabel=ffa657&sideLabels=c9d1d9&dates=8b949e"><img src="https://streak-stats.demolab.com/?user=mohamedaminehamdi&background=f6f8fa&border=d0d7de&stroke=d0d7de&ring=953800&fire=953800&currStreakNum=24292f&sideNums=24292f&currStreakLabel=953800&sideLabels=24292f&dates=8b949e" alt="Total contributions and current streak"></picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/mohamedaminehamdi/mohamedaminehamdi/output/github-snake-dark.svg">
    <img alt="Snake eating my contribution graph" src="https://raw.githubusercontent.com/mohamedaminehamdi/mohamedaminehamdi/output/github-snake.svg">
  </picture>
</p>

I keep fleets of embedded devices reachable, patched and trusted, and I automate the platform around them. By day that means secure remote access, WireGuard mesh networking and Kubernetes at [EcoG](https://www.ecog.io) in Munich. On the side I build local-first AI tools and write about what I learn along the way.

<details>
<summary><b>A pattern I build: secure access to devices in the field</b></summary>
<br>

Every device stays reachable without ever being exposed to the internet. Engineers authenticate once, policies decide which device they can reach, and a hardened fallback path exists for when the mesh is down.

```mermaid
flowchart LR
  eng([Engineer]) -->|SSO and MFA| idp[Identity provider]
  idp --> cp[Mesh control plane]
  cp -.->|access policies| fleet
  eng ==>|WireGuard mesh| fleet
  eng -->|fallback| bridge[Hardened SSH bridge]
  bridge -->|per-device tunnel| fleet
  subgraph fleet[Field device fleet]
    d1[Device]
    d2[Device]
    d3[Device]
  end
  fleet -->|Telegraf| prom[Prometheus] --> graf[Grafana]
  git[(Git: Terraform and Ansible)] -->|CI/CD| cp
  git -->|CI/CD| bridge
```

</details>

## Stack

<p align="center">
  <a href="https://mohamedaminehamdi.github.io/mohamedaminehamdi/"><picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/stack-sphere-dark.svg">
    <img src="assets/stack-sphere-light.svg" width="100%" alt="Rotating 3D sphere of my stack: Kubernetes, Helm, Argo CD, Docker, Harbor, Istio, Cilium, Traefik, Nginx, Terraform, Ansible, Packer, Vault, AWS, Cloudflare, Linux, Bash, GitHub Actions, GitLab CI, Jenkins, Git, GitHub, Trivy, SonarQube, Snyk, OWASP, Falco, Keycloak, WireGuard, Prometheus, Grafana, OpenTelemetry, InfluxDB, Go, Python, TypeScript, JavaScript, Node.js, NestJS, Next.js, React, PostgreSQL, MongoDB, Tailwind CSS, Prisma, Supabase, Vercel">
  </picture></a>
  <br><sub>Click the sphere for the interactive version: hover a logo to enlarge it, drag to spin.</sub>
</p>

## GitHub activity

<picture><source media="(prefers-color-scheme: dark)" srcset="profile-3d-contrib/profile-night-rainbow-animate.svg"><img src="profile-3d-contrib/profile-green-animate.svg" alt="3D contribution graph with contribution radar and languages" width="100%"></picture>

<p align="center">
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api?username=mohamedaminehamdi&show_icons=true&include_all_commits=true&count_private=true&rank_icon=github&bg_color=161b22&title_color=ffa657&text_color=c9d1d9&icon_color=3fb950&border_color=30363d&ring_color=ffa657"><img src="https://github-readme-stats.vercel.app/api?username=mohamedaminehamdi&show_icons=true&include_all_commits=true&count_private=true&rank_icon=github&bg_color=f6f8fa&title_color=953800&text_color=24292f&icon_color=1a7f37&border_color=d0d7de&ring_color=953800" alt="GitHub stats" height="180"></picture>
  <picture><source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api/top-langs/?username=mohamedaminehamdi&layout=compact&langs_count=8&bg_color=161b22&title_color=ffa657&text_color=c9d1d9&border_color=30363d"><img src="https://github-readme-stats.vercel.app/api/top-langs/?username=mohamedaminehamdi&layout=compact&langs_count=8&bg_color=f6f8fa&title_color=953800&text_color=24292f&border_color=d0d7de" alt="Top languages" height="180"></picture>
</p>

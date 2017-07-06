import web
import ssh
import scripts


urls = (
	"/", "Main",
	"/setup", "SetupTool",
	"/automation", "Automation",
	"/links", "Links",
	"/team_page", "TeamPage",
	"/about", "About"
)

render = web.template.render("templates/")

app = web.application(urls, globals())

def base(contant, tool_style="", path="Not Specified", user_name="Guest", prompt=None):
	grid_layout = render.base.grid_layout(contant=contant)
	navigation = render.base.navigation()
	user_name = user_name
	path = path
	footer = render.base.footer()
	
	return render.base.layout(grid_layout=grid_layout,
						 navigation=navigation,
						 user_name=user_name,
						 path=path,
						 footer=footer,
						 tool_style=tool_style)


class Main(object):
	
	def GET(self):
		return base(render.content.main(), path="Home/News")
		

	def POST(self):
		return web.seeother("Index")


class SetupTool(object):
	
	def GET(self):
		
		return base(render.content.setup(), "setup.css", "Setup Tools")

	def POST(self):
		
		# Get data from the HTML form.
		form = web.input(selected_scripts=[])
		dut = ssh.DUT(form.ipaddr, form.user_name, form.passwd, form.oc)
		user_scripts = form.selected_scripts
		
		if form.console != "None":
			# Create the Console object to communicate with it.
			console_credentials = form.console.split('/')
			console = ssh.Console(console_credentials[0], 
								  console_credentials[1], 
								  console_credentials[2])
			
			console.first_setup(dut.ipaddr, dut.oc)
		else:
			pass
			
		
		
		# Change shell to Bash
		dut.change_to_bash()
		# Set interfaces - Orens' script
		
		
		# Connectivity Check - Misha Script
		
		# Put selected scripts in /home/admin/
		for script_name in user_scripts:
			dut.send_file(scripts.db[script_name])
		# Collect appliance information		
		
		# 
		
		return base(render.content.setup(), "setup.css", "Setup Tools - After POST")


class Automation(object):
	
	def GET(self):
		return base(render.content.in_construction(), path="Automation")
		

	def POST(self):
		return web.seeother("")


class Links(object):
	
	def GET(self):
		return base(render.content.in_construction(), path="Usful Links")
		

	def POST(self):
		return web.seeother("")


class TeamPage(object):
	
	def GET(self):
		return base(render.content.in_construction(), path="Team Page")
		

	def POST(self):
		return web.seeother("")


class About(object):
	
	def GET(self):
		return base(render.content.in_construction(), path="About this page")
		

	def POST(self):
		return web.seeother("")


###########################
####   Run The Server   ###
###########################

if __name__ == "__main__":
	app.run()
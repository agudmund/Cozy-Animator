using Microsoft.Extensions.DependencyInjection;

namespace CozyMaui;

public partial class App : Application
{
	public App()
	{
		InitializeComponent();
	}

	protected override Window CreateWindow(IActivationState? activationState)
	{
	    Window window = new Window(new AppShell());
	    
	    // ✨ Our cozy title, just like the Python version
	    window.Title = "Cozy Frame Renderer";
	    
	    return window;
	}
	
}
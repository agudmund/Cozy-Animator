namespace CozyMaui;

public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();

        textEditor.TextChanged += OnTextChanged;

        fontSlider.ValueChanged += (s, e) =>
        {
            textEditor.FontSize = fontSlider.Value;
        };

        textEditor.FontSize = fontSlider.Value;
    }

    private void OnTextChanged(object? sender, TextChangedEventArgs e)
    {
        var text = textEditor.Text?.Trim() ?? string.Empty;

        int words = string.IsNullOrWhiteSpace(text) ? 0 : text.Split(new[] { ' ', '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries).Length;
        int chars = text.Length;
        countLabel.Text = $"Words: {words} • Characters: {chars}";

        previewLabel.Text = string.IsNullOrWhiteSpace(text) 
            ? "Your beautiful animation will appear here..." 
            : text;
    }

    // Top bar icons
    private async void OnLogClicked(object sender, EventArgs e)
    {
        await DisplayAlertAsync("📜 Log", "Log viewer coming soon! 🌱", "OK");
    }

    private async void OnFeaturesClicked(object sender, EventArgs e)
    {
        await DisplayAlertAsync("📋 Features", "Feature list coming soon! 🌱", "OK");
    }

    private async void OnSettingsClicked(object sender, EventArgs e)
    {
        await DisplayAlertAsync("⚙ Settings", "Settings page coming soon! 🌱", "OK");
    }

    // Bottom buttons
    private async void OnGenerateClicked(object sender, EventArgs e)
    {
        await DisplayAlertAsync("🎉 Generate", "PNG sequence generation coming soon! 🌱", "OK");
    }

    private void OnClearClicked(object sender, EventArgs e)
    {
        textEditor.Text = string.Empty;
    }

    private async void OnPauseClicked(object sender, EventArgs e)
    {
        await DisplayAlertAsync("⏸ Pause", "Preview pause coming soon! 🌱", "OK");
    }
}
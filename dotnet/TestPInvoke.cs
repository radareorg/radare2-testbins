using System;
using System.Runtime.InteropServices;

class Program
{
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int MessageBox(IntPtr hWnd, string text, string caption, uint type);

    [DllImport("kernel32.dll")]
    public static extern int GetCurrentProcessId();

    static void Main()
    {
        Console.WriteLine("PID: " + GetCurrentProcessId());
        MessageBox(IntPtr.Zero, "Hello", "Test", 0);
    }
}
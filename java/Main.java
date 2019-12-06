import java.io.BufferedReader;
import java.io.FileReader;

public class Main {
	public static void main(String[] args) {
		System.out.println("Hello World");
		String filename = "/etc/services";
		try {
			BufferedReader reader = new BufferedReader(new FileReader(filename));
			String line;
			while ((line = reader.readLine()) != null) {
				System.out.println ("Line: " + line);
			}
			reader.close();
		} catch (Exception e) {
			System.err.format("Exception occurred trying to read '%s'.", filename);
			e.printStackTrace();
		}
	}
}

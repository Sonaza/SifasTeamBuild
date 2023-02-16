#include <cstdio>
#include <cstdlib>
#include <csignal>

void signal_handler(int signal)
{
	// gSignalStatus = signal;
	printf("ASDFKLSDKSLDKSLDFKSDF %d\n", signal);
}

int main()
{
	// Catch signals to do nothing because the Python script should be handling those
	std::signal(SIGINT, signal_handler);
	std::signal(SIGTERM, signal_handler);
	std::system("pipenv run python BuildCardRotations.py --watch");
	return 0;
}

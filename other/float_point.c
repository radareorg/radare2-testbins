float sum_float(float a, float b)
{
  return a + b;
}

double sum_double(double a, double b)
{
  return a + b;
}

int main()
{
  float f = sum_float(1, 2);
  double d = sum_double(1, 2);
  return f == d;
}

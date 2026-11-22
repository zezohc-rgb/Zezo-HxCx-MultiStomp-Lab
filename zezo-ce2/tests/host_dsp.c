/* Static fixtures and a non-PIE host executable mirror the 32-bit ABI words. */
#include <assert.h>
#include <math.h>
#include "zezo_ce2.c"

static unsigned int ctx[13], source = 42, destination, destination_ptr, desc[3];
static float params[7], audio[16];
static union {
    State state;
    unsigned int words[sizeof(State) / 4 + N + 2];
} memory;

static unsigned int address(void *p)
{
    assert((uintptr_t)p <= UINT32_MAX);
    return (unsigned int)(uintptr_t)p;
}

static void reset(float rate, float depth)
{
    memory.state.magic = 0;
    params[0] = 1.0f;
    params[5] = rate;
    params[6] = depth;
    for (unsigned int i = 0; i < N / CLEAR_STEP; ++i)
        Fx_DLY_ZezoCE2(ctx);
    assert(memory.state.ready == 1 && memory.state.write == 0);
    assert(destination == source);
}

static float render(float rate, float depth, float frequency, float amplitude,
                    int stereo, float *peak)
{
    reset(rate, depth);
    float energy = 0.0f;
    *peak = 0.0f;
    for (int block = 0; block < 2048; ++block) {
        float input[8];
        for (int i = 0; i < 8; ++i) {
            input[i] = amplitude * sinf(6.2831853f * frequency * (8 * block + i) / 44100.0f);
            audio[i] = stereo == 1 ? 0.0f : input[i];
            audio[i + 8] = stereo == 2 ? -input[i] : input[i];
        }
        Fx_DLY_ZezoCE2(ctx);
        for (int i = 0; i < 8; ++i) {
            assert(isfinite(audio[i]) && isfinite(audio[i + 8]));
            if (stereo == 0)
                assert(audio[i] == audio[i + 8]);
            if (stereo == 2)
                assert(fabsf(audio[i] - 0.5f * input[i]) < 1e-6f);
            float wet = audio[i] - (stereo == 1 ? 0.0f : 0.5f * input[i]);
            if (block >= 256)
                energy += wet * wet;
            *peak = fmaxf(*peak, fmaxf(fabsf(audio[i]), fabsf(audio[i + 8])));
        }
    }
    return sqrtf(energy / ((2048 - 256) * 8));
}

static int impulse_peak(float depth, float phase)
{
    reset(0.0f, depth);
    float peak = 0.0f;
    int peak_index = -1;
    for (int start = 0; start < 320; start += 8) {
        memory.state.phase = phase;
        memory.state.lfo = phase < 0.5f ? -1.0f : 1.0f;
        for (int i = 0; i < 16; ++i)
            audio[i] = start == 0 && (i == 0 || i == 8) ? 0.1f : 0.0f;
        Fx_DLY_ZezoCE2(ctx);
        for (int i = 0; i < 8; ++i) {
            if (start + i > 0 && fabsf(audio[i]) > peak) {
                peak = fabsf(audio[i]);
                peak_index = start + i;
            }
        }
    }
    return peak_index;
}

static void check_circuit_models(void)
{
    const double pi = 3.141592653589793;
    for (int hz = 1000; hz <= 17000; hz += 1000) {
        double omega = 2.0 * 44100.0 * tan(pi * hz / 44100.0);
        double real = 1.0 - 1.081e-9 * omega * omega;
        double imag = omega * (4.71e-5 - 1.27182e-14 * omega * omega);
        double expected = 1.0 / hypot(real, imag);
        BbdFilter state = {0};
        double energy = 0;
        for (int i = 0; i < 45080; ++i) {
            float y = bbd_filter(&state, sin(2.0 * pi * hz * i / 44100.0));
            if (i >= 980)
                energy += y * y;
        }
        assert(fabs(sqrt(2.0 * energy / 44100.0) - expected) < 1e-5);
    }
    for (int i = -100; i <= 100; ++i) {
        float lfo = i * 0.01f;
        double expected = 171.99 + 318.36672 * log1p(-0.11 * lfo);
        assert(fabs(bbd_delay(1.0f, lfo) - expected) < 0.0001);
        assert(bbd_delay(0.0f, lfo) == 171.99f);
    }
}

int main(void)
{
    check_circuit_models();
    ctx[1] = address(params);
    ctx[3] = address(desc);
    ctx[5] = address(audio);
    ctx[11] = address(&destination_ptr);
    ctx[12] = address(&source);
    destination_ptr = address(&destination);
    desc[0] = address(&memory);
    desc[1] = desc[0] + sizeof(memory);
    desc[2] = sizeof(memory);

    /* An undersized allocation and bypass both leave audio alone. */
    unsigned int span = desc[2];
    desc[2] = 0;
    params[0] = 1.0f;
    audio[0] = 0.25f;
    Fx_DLY_ZezoCE2(ctx);
    assert(memory.state.magic == 0 && audio[0] == 0.25f);
    desc[2] = span;
    params[0] = 0.0f;
    Fx_DLY_ZezoCE2(ctx);
    assert(memory.state.magic == 0 && audio[0] == 0.25f);

    float peak;
    float mid = render(0.5f, 0.0f, 440.0f, 0.1f, 0, &peak);
    assert(mid > 0.02f && peak < 0.11f);
    assert(render(0.5f, 0.0f, 440.0f, 0.1f, 1, &peak) > 0.4f * mid);
    assert(render(0.5f, 1.0f, 440.0f, 0.1f, 2, &peak) < 1e-6f);
    assert(render(0.5f, 0.0f, 10000.0f, 0.1f, 0, &peak) < 0.6f * mid);
    assert(render(0.5f, 0.0f, 10.0f, 0.1f, 0, &peak) < 0.2f * mid);

    float small = render(0.0f, 0.0f, 2200.0f, 0.05f, 0, &peak);
    assert(fabsf(render(0.0f, 0.0f, 2200.0f, 0.1f, 0, &peak) - 2.0f * small) < 1e-6f);
    assert(render(0.0f, 0.0f, 2200.0f, 1.0f, 0, &peak) < 18.0f * small);

    render(0.0f, 1.0f, 440.0f, 0.15f, 0, &peak);
    assert(fabsf(memory.state.phase - (3.560606f / 11.0f) * 16384.0f / 44100.0f) < 0.001f);
    render(1.0f, 1.0f, 440.0f, 0.15f, 0, &peak);
    assert(fabsf(memory.state.phase - (3.560606f * 16384.0f / 44100.0f - 1.0f)) < 0.001f);

    int fixed = impulse_peak(0.0f, 0.0f);
    assert(fixed >= 172 && fixed < 182);
    assert(impulse_peak(0.0f, 0.5f) == fixed);
    int shortest = impulse_peak(1.0f, 0.5f);
    int longest = impulse_peak(1.0f, 0.0f);
    assert(shortest >= 135 && shortest < 145);
    assert(longest >= 205 && longest < 215);

    reset(0.5f, 0.0f);
    params[5] = 1.0f;
    params[6] = 1.0f;
    Fx_DLY_ZezoCE2(ctx);
    assert(memory.state.rate > 0.5f && memory.state.rate < 0.51f);
    assert(memory.state.depth > 0.0f && memory.state.depth < 0.01f);
    memory.state.phase = NAN;
    Fx_DLY_ZezoCE2(ctx);
    assert(memory.state.phase > 0.0f && memory.state.phase < 0.001f);
    return 0;
}

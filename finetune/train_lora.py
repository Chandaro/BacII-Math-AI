"""mlx_lm.lora with a capped buffer cache and a memory log. Usage: train_lora.py <cache_gb> <lora args...>"""
import sys, threading, time
import mlx.core as mx
gb = float(sys.argv.pop(1))
mx.set_cache_limit(int(gb * 1024**3))
def watch():
    while True:
        time.sleep(15)
        print(f"MEM active {mx.get_active_memory()/1e9:.1f} cache {mx.get_cache_memory()/1e9:.1f} peak {mx.get_peak_memory()/1e9:.1f} GB", flush=True)
threading.Thread(target=watch, daemon=True).start()
print("device limit GB", mx.device_info().get("max_recommended_working_set_size", 0) / 1e9, flush=True)
from mlx_lm.lora import main
main()

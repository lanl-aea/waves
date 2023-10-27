title "Flow in a simple box"
inciter

  term 0.11  # Max physical time, s
  ttyi 10  # TTY output interval
  cfl 0.8
  scheme alecg

  partitioning
    algorithm rcb
  end

  compflow
    physics euler
    problem user_defined

    # Units: m,kg,s,
    ic
      density 0.912 end  # kg/m^3
      velocity 0.0 0.0 0.0 end  # m/s
      pressure 77816.5 end  # Initiate linear
    end

    material
      gamma 1.4 end
      cv 717.5 end
    end

    bc_sym
      sideset 1 2 3 5 end
    end

    bc_farfield  # Outlet
      sideset 6 end
      density 0.912
      velocity 0.0 0.0 0.0 end
      pressure 77816.5
    end

    bc_timedep  # Inlet
      sideset 4 end
      fn # t       p   rho x-vel y-vel z-vel
         0.0 77816.5 0.912 0.000 0.000 0.000
         0.1 77816.5 0.912 5.000 0.000 0.000
        10.0 77816.5 0.912 5.000 0.000 0.000
      end
    end
  end

  history_output
    interval 1
    point p1 0.5 0.25 0.25 end
  end

  field_output
    time_interval 0.001
    var node
      density
      x-velocity
      y-velocity
      z-velocity
      specific_total_energy
      pressure
    end
  end

  diagnostics
    interval  250
    format    scientific
    error     l2
  end

end

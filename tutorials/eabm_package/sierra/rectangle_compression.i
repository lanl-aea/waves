begin sierra

  begin function line
    type is analytic
    evaluate expression = "x"
  end function line

  begin property specification for material mock
    density = 0.27000e-08
    begin parameters for model elastic
      youngs modulus = 100
      poissons ratio = 0.3
    end
  end

  begin shell section planestress
    thickness = 0.1
  end shell section planestress

  begin finite element model rectangle_compression
    database name = rectangle_mesh.g
    database type = exodusII

    begin parameters for block ELEMENTS
      material mock
      solid mechanics use model elastic
      section = planestress
    end

  end finite element model rectangle_compression

  begin adagio procedure adagio

    begin time control
      begin time stepping block p0
        start time = 0
        begin parameters for adagio region adagio
            time increment = 0.5
        end
      end
      termination time = 1
    end

    begin adagio region adagio
      use finite element model rectangle_compression

      begin results output output_rectangle_compression
        database name = rectangle_compression.e
        database type = exodusII
        at time 0 interval = 0.1
        global variables = kinetic_energy
        global variables = internal_energy
        global variables = external_energy
        global variables = von_mises_max
        global variables = effective_strain_max
        nodal variables = displacement
        nodal variables = force_external
        nodal variables = force_internal
        element variables = strain
        element variables = unrotated_stress
        element variables = effective_strain
        element variables = von_mises
      end

      begin user output
        include all blocks
        compute global von_mises_max as max absolute value of element von_mises
        compute global effective_strain_max as max absolute value of element effective_strain
      end user output

      begin fixed displacement
        node set = bottom_left
        component = x
      end

      begin fixed displacement
        node set = bottom_left
        component = y
      end

      begin fixed rotation
        node set = bottom_left
        component = x
      end

      begin fixed rotation
        node set = bottom_left
        component = y
      end

      begin fixed rotation
        node set = bottom_left
        component = z
      end

      begin fixed displacement
        node set = bottom
        component = y
      end

      begin prescribed displacement
        node set = top
        component = y
        function = line
        scale factor = -0.01
      end

      ## TODO: Do we need to add traction BC for plane stress? Is there a plane stress element?

      begin solver
        begin cg
          reference = external
          target relative residual = 1e-10
          begin full tangent preconditioner
            iteration update = 10
          end full tangent preconditioner
        end cg
      end solver

    end adagio region adagio

  end adagio procedure adagio

end sierra

from renderer.renderer import *


def reflect(ray_direction, planeNormal, plate=None):
    perp = 2 * ray_direction.dot(planeNormal)
    reflectDir =ray_direction - (perp * planeNormal)

    return reflectDir


def refract(uv, n, new_ior, previous_ior=1):
    n = -n.copy()
    ni_over_nt = previous_ior / new_ior
    dt = np.dot(uv, n)
    discriminant = 1 - ni_over_nt * ni_over_nt * (1 - dt**2)
    refractDir = ni_over_nt * (uv-n*dt) - n*sqrt(abs(discriminant))

    return refractDir


def generate_rand_vec(bound):
    vector_i = np.array([0, 1, 0])

    vector_f = rotate(vector_i, *calc_matrixes(0, 0, np.random.uniform(-bound, bound)))
    vector_f = rotate(vector_f, *calc_matrixes(0, np.random.uniform(0, 360), 0))

    return vector_f


def add_direction_noise(vector, bound):
    generated_vec = generate_rand_vec(bound)

    y_angle = atan2(vector[2], vector[0])
    z_angle = acos(vector[1])

    vector_f = rotate(generated_vec, *calc_matrixes(0, 0, z_angle/pi*180))
    vector_f = rotate(vector_f, *calc_matrixes(0, y_angle/pi*180, 0))

    return vector_f


def get_hdri_color(hdri, ray_direction):
    ray_direction /= np.linalg.norm(ray_direction)
    x = (atan2(ray_direction[2], ray_direction[0]) / (2 * pi) + 0.5) * (hdri.shape[1] - 1)
    y = acos(ray_direction[1]) / pi * hdri.shape[0]

    return hdri[floor(y)][floor(x)].copy().astype('float64')


def load_hdri(path):
    return cv2.cvtColor(cv2.flip(cv2.imread(path), 0), cv2.COLOR_RGB2BGR)


def calculate_shadow(ray_direction, plate, hit_point):
    light_multipliers = []
    for l in rend_info['LIGHTS']:
        if l.is_on:
            direct_lighting_factor = 0.2

            light_color = color2rgb(l.color)
            light_ray_direction = np.array([l.x, -l.y, l.z]) - hit_point
            distance = np.linalg.norm(light_ray_direction)
            light_ray_direction /= distance

            if l.lighting_angle < 360 and l.direction is not None:
                direction = l.direction.copy()
                direction[1] *= -1
                dot_prod = light_ray_direction.dot(direction)
                if (dot_prod + 1) * 180 <= l.lighting_angle:
                    in_light_beam = np.clip(-dot_prod, 0.7, 1)
                else:
                    in_light_beam = np.clip(l.size * (-dot_prod - (l.lighting_angle / 180 - 1))**2 / 5, 0, 0.7)
            else:
                in_light_beam = 1

            if in_light_beam != 0:
                if type(plate) != DustParticle and plate.transparency == 0:
                    sign1 = copysign(1, ray_direction.dot(plate.planeNormal))
                    sign2 = copysign(1, light_ray_direction.dot(plate.planeNormal))
                    self_intersect = (sign1 == sign2)  # 'invalid self-intersection',
                    #                                     makes shadows side-dependent
                else:
                    self_intersect = False

                if not self_intersect:
                    hits = getRayHit(light_ray_direction, hit_point, except_=plate, except_lights=True,
                                     max_distance=distance, return_bool=True)

                    did_hit = hits[0] if type(hits) == list else hits
                    transparent_hits = hits[1] if type(hits) == list and len(hits[1]) > 0 else False
                    total_transparency = np.min(
                        [p[0].transparency / 100 for p in transparent_hits]) if transparent_hits else 1

                    if not did_hit:
                        # If directly lit
                        # Shade according to lighting angle
                        if type(plate) != DustParticle:
                            direct_lighting_factor = abs(light_ray_direction.dot(plate.planeNormal))
                            direct_lighting_factor = np.clip(direct_lighting_factor, 0.5, 1)
                            direct_lighting_factor = np.clip(direct_lighting_factor * total_transparency, 0.2, 1)
                            if plate.transparency != 0:
                                direct_lighting_factor = np.clip(direct_lighting_factor * (plate.transparency / 100),
                                                                 0.2, 1)
                        else:
                            direct_lighting_factor = 0.75

                        if transparent_hits:
                            for p in transparent_hits:
                                if p[0].project_color != 0:
                                    # The more transparent, the more:
                                    # 1) color of the object;
                                    # 2) color of the light; will pass through
                                    # light_color += (p[1] - light_color) * (1 - p[0].transparency / 100) / 2
                                    project = p[0].project_color / 100
                                    light_color += (p[1] - light_color) * ((1 - p[0].transparency / 100) * project)
                                    light_color += (color2rgb(l.color) - light_color) * \
                                                   ((1 - p[0].transparency / 100) * project)

            # Influence of distances are divided by 10 and pulled towards 20
            light_multipliers.append(light_color / 255 * direct_lighting_factor * in_light_beam * (
                    l.brightness / (20 - (20 - max(min(distance, 15), 0.5) ** 2) / 10)))

    shadow_multiplier = sum(light_multipliers)
    return shadow_multiplier + (1 - shadow_multiplier) * (1 - plate.shadows / 100)


def getRayHit(rayDirection, rayPoint, max_distance=inf, return_bool=False, return_coord=False, return_color=False,
              return_distance=False, skip_transparent=False, except_=None, except_lights=False, camera=None):
    # Loop through all objects
    hit_plate = None
    hit_point = None
    hit_color = None
    transparent_hits = []
    record_distance = inf
    for plate in rend_info["PLATES"] + rend_info["SPHERES"]:
        case1 = type(plate) == Plate and (plate.is_sphere_indicator or plate == except_ or plate.is_camera_box == camera
                                          or (type(plate.is_camera_box) == Light and except_lights))
        case2 = (plate.transparency > 0 and skip_transparent)
        if case1 or case2 or not plate.ray_tracer_visible:
            continue

        point, distance = plate.find_intersection(rayDirection, rayPoint, max_distance, record_distance, except_)
        if point is not None:
            color = plate.getColor(plate, *point)
            if color is not None:
                if return_bool:
                    if plate.transparency != 0:
                        if 0 < plate.transparency < 100:  # semi-transparent
                            transparent_hits.append([plate, color2rgb(plate.getColor(plate, *point))])
                        if plate.transparency == 0:
                            return [True, []]
                    else:
                        return True

                hit_plate = plate
                hit_point = point
                hit_color = np.array(color).astype('float32')
                record_distance = distance

    if return_bool:
        if len(transparent_hits) == 0:
            return
        else:
            return [False, transparent_hits]

    return_ = [hit_plate]
    if return_coord:
        return_.append(hit_point)
    if return_color:
        return_.append(hit_color)
    if return_distance:
        return_.append(record_distance)

    return return_


def getRayColor(ray_direction, ray_point, canvas, except_=None, max_bounces=0, camera=None,
                ior=1, add_RGB=1):
    # Get hit plate
    plate, hit_point, color, distance = getRayHit(ray_direction, ray_point, return_coord=True, return_color=True,
                                                  return_distance=True, except_=except_,
                                                  skip_transparent=(max_bounces <= 0), camera=camera)

    if color is not None:
        current_color = color + add_RGB  # +value so it's not 100% absorbent
    else:
        if camera.hdri is None:
            current_color = canvas.color.copy()
        else:
            current_color = get_hdri_color(camera.hdri, ray_direction)

    if plate:
        if type(plate) == Sphere:
            plate.planeNormal = (np.array([plate.x, plate.y, plate.z]) - hit_point) / plate.radius
        ray_side = copysign(1, ray_direction.dot(plate.planeNormal))
        plate.planeNormal *= ray_side
        not_inside_bounce = (plate.volume and plate.transparency != 0 and ray_side < 0)

        # Reflection
        if max_bounces >= 1 and plate.reflectiveness != 0 and not not_inside_bounce:
            reflectDir_i = reflect(ray_direction, plate.planeNormal)

            for _ in range(plate.num_ray_splits if plate.roughness != 0 else 1):
                if plate.roughness != 0:
                    reflectDir = add_direction_noise(reflectDir_i, plate.roughness / 100 * 180)
                else:
                    reflectDir = reflectDir_i

                reflect_color = getRayColor(reflectDir, hit_point, canvas, max_bounces=max_bounces-1,
                                            except_=plate, camera=camera, add_RGB=add_RGB)
                current_color += (reflect_color.reshape(3) - current_color) * \
                                 (plate.reflectiveness / 100 / (plate.num_ray_splits if plate.roughness != 0 else 1))

        # Refraction
        if plate.transparency != 0:
            if plate.volume:
                if plate.ior == ior:
                    refractDir_i = refract(ray_direction, plate.planeNormal, 1, previous_ior=plate.ior)
                else:
                    refractDir_i = refract(ray_direction, plate.planeNormal, plate.ior, previous_ior=ior)
            else:
                refractDir_i = refract(ray_direction, -plate.planeNormal, plate.ior, previous_ior=ior)

            for _ in range(plate.num_ray_splits if plate.roughness != 0 else 1):
                if plate.roughness != 0:
                    refractDir = add_direction_noise(refractDir_i, plate.roughness / 100 * 180)
                else:
                    refractDir = refractDir_i

                if plate.volume:
                    if plate.ior == ior:
                        arguments = [refractDir, hit_point, 1]
                    else:
                        arguments = [refractDir, hit_point, plate.ior]
                else:
                    arguments = [ray_direction, hit_point + -refractDir * plate.thickness, 1]

                refract_color = getRayColor(arguments[0], arguments[1], canvas, max_bounces=max_bounces - 1,
                                            except_=plate, camera=camera,
                                            ior=arguments[2], add_RGB=add_RGB)
                current_color += (refract_color.reshape(3) - current_color) * \
                                 (plate.transparency / 100 / (plate.num_ray_splits if plate.roughness != 0 else 1))

        # Shadows and highlights
        if plate.shadows != 0 and max_bounces >= 0:
            shadow_multiplier = calculate_shadow(ray_direction, plate, hit_point)
            current_color *= shadow_multiplier

    # Volumetric lighting
    if camera.volumetric_activated or camera.volumetric_particle.density != 0:
        distance = min(distance, camera.max_volumetric_distance) if distance != inf else camera.max_volumetric_distance
        total_steps = int(distance * camera.volumetric_checks)
        # (Upper bound: distance-0.01, to prevent dust-particles from intersecting plate)
        for t in np.linspace(distance - 0.01, 0, total_steps):
            dust_coord = ray_point + t * ray_direction
            dust_color = color2rgb(camera.volumetric_particle.getColor(camera.volumetric_particle, *dust_coord))

            if camera.volumetric_particle.visible and camera.volumetric_particle.density != 0:
                dust_shadow_multiplier = np.array([1, 1, 1])
                if camera.volumetric_particle.shadows != 0 and max_bounces >= 0:
                    dust_shadow_multiplier = calculate_shadow(ray_direction, camera.volumetric_particle, dust_coord)

                dust_color *= dust_shadow_multiplier
                amount = camera.volumetric_particle.density / 100 / camera.volumetric_checks

                current_color += (dust_color - current_color) * amount

    pixel_color = np.clip(current_color, 0, 255)
    # pixel_color = np.clip(shadow_multiplier * 255, 0, 255)  # Debugging

    return pixel_color


def create_photo(canvas, camera, display=False, frame=None, resize=True):
    if frame is None:
        frame = camera.frame

    image = PIL.Image.fromarray(frame.astype(np.uint8))
    tk = rend_info['WINDOWS'][camera.displaying][1]
    if resize:
        camera.photo = PIL.ImageTk.PhotoImage(image=image.resize((canvas.winfo_width(), canvas.winfo_height())), master=tk)
    else:
        camera.photo = PIL.ImageTk.PhotoImage(image=image, master=tk)

    if display:
        canvas.delete('all')
        canvas.create_image(0, 0, image=camera.photo, anchor=NW)


def rayTrace(camera, output, preview_mode, update_frequency_in_pixels, max_bounces, resize, add_RGB=1):
    if camera.is_on:
        c = camera
        start_time = time.time()
        name = c.displaying
        canvas = rend_info['WINDOWS'][name][1]
        camera_pos = np.array([c.x, c.y, c.z])

        # Clear frame
        c.init_frame(*c.resolution)

        # Prepare color
        for plate in rend_info["PLATES"] + rend_info["SPHERES"]:
            plate.fill = color2rgb(plate.fill)

        # Find pixel colors
        count = 0
        total = c.resolution[0] * c.resolution[1]

        # Calculate x, y and z angles from local angles
        c.xrot_, c.yrot_, c.zrot_ = calc_matrixes(0, -c.yangle, 0)

        if preview_mode in ['REFINE', 'REFINE_SCANNER']:
            refinement = max(c.resolution) / 20
            temp_res = (np.array(c.resolution) / refinement).astype(np.uint8)
            temp_frame = c.init_frame(*temp_res, return_=True)
        else:
            refinement = 1

        last_time_ = time.time()
        while refinement >= 1:
            if preview_mode in ['REFINE', 'REFINE_SCANNER']:
                temp_res = (np.array(c.resolution) / refinement).astype(int)
                temp_frame = cv2.resize(temp_frame, tuple(temp_res), interpolation=0)

            if resize:
                ratio = canvas.winfo_width() / canvas.winfo_height()
                multiplier_x = c.fov / c.resolution[0] * ratio
                multiplier_y = c.fov / c.resolution[1]
            else:
                multiplier_x = c.fov / min(c.resolution)
                multiplier_y = c.fov / min(c.resolution)

            for iy, y_init in enumerate(np.arange(0, c.resolution[1], refinement)):
                for ix, x_init in enumerate(np.arange(0, c.resolution[0], refinement)):
                    x, y = floor(x_init), floor(y_init)
                    if c.frame_filled_in[c.resolution[1] - y - 1, x] == 0:
                        # Grid positions in 3D
                        x_ = c.x + x * multiplier_x - c.resolution[0] / 2 * multiplier_x
                        y_ = c.y + y * multiplier_y - c.resolution[1] / 2 * multiplier_y
                        z_ = c.z + 2  # Distance of grid from camera

                        # Apply local rotation
                        if c.zangle != 0:
                            x_, y_ = rotate_2D(x_, y_, c.x, c.y, c.zangle)
                        if c.xangle != 0:
                            y_, z_ = rotate_2D(y_, z_, c.y, c.z, c.xangle)

                        xx, yy, zz = rotate(np.array([x_, y_, z_]), c.xrot_, c.yrot_, c.zrot_,
                                            center=camera_pos)  # Y-rotation

                        rayDirection = np.array([xx, yy, zz]) - camera_pos
                        rayDirection /= np.linalg.norm(rayDirection)
                        ray_point = camera_pos.copy()
                        ray_point[1] *= -1
                        rayDirection[1] *= -1

                        pixel_color = getRayColor(rayDirection, ray_point, canvas, max_bounces=max_bounces,
                                                  camera=camera, add_RGB=add_RGB)

                        if pixel_color is None:
                            pixel_color = c.color

                        c.frame_filled_in[c.resolution[1] - y - 1, x] = 1
                        count += 1
                    else:
                        pixel_color = c.frame[c.resolution[1] - y - 1, x]

                    c.frame[c.resolution[1] - y - 1, x] = pixel_color

                    if preview_mode in ['REFINE', 'REFINE_SCANNER']:
                        if 0 <= temp_res[1] - iy - 1 < temp_res[1] and 0 <= ix < temp_res[0]:
                            temp_frame[temp_res[1] - iy - 1, ix] = pixel_color

                    if count % update_frequency_in_pixels == 0:
                        if preview_mode == 'SCANNER':
                            create_photo(canvas, c, display=True, resize=resize)
                        if preview_mode == 'REFINE_SCANNER':
                            create_photo(canvas, c, display=True, frame=temp_frame, resize=resize)
                        freeze_update()

                    if time.time() - last_time_ >= 1:
                        print(f'{round(count / total * 100, 2)}% FINISHED RENDERING...')
                        last_time_ = time.time()

            if refinement > 1 > refinement - 1:
                refinement = 1
            else:
                refinement -= 1

            if preview_mode == 'REFINE':
                create_photo(canvas, c, display=True, frame=temp_frame, resize=resize)
                freeze_update()

        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(elapsed_time, 60)
        print(f'100.0% FINISHED RENDERING IN {minutes} MINUTES AND {round(seconds, 2)} SECONDS')

        create_photo(canvas, c, display=True, resize=resize)
        freeze_update()

        if output:
            if resize:
                dim = (canvas.winfo_width(), canvas.winfo_height())
                frame = cv2.resize(c.frame.astype('uint8'), dim, interpolation=cv2.INTER_AREA)
            else:
                frame = c.frame.astype('uint8')

            cv2.imwrite(output, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
